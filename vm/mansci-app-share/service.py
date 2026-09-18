"""Authenticated, temporary reverse-proxy registry for ManSci classroom apps."""
from __future__ import annotations

import json
import os
from pathlib import Path
import pwd
import re
import secrets
import time

from jupyterhub.services.auth import HubOAuthenticated, HubOAuthCallbackHandler
from tornado import web
from tornado.ioloop import IOLoop, PeriodicCallback

SERVICE_PREFIX = os.environ.get(
    "JUPYTERHUB_SERVICE_PREFIX", "/services/mansci-app-share/"
).rstrip("/") + "/"
CLASSROOM_COOKIE = "mansci-app-share-session"
LISTEN_PORT = int(os.environ.get("MANSCI_APP_SHARE_PORT", "8999"))
MAX_AGE = 12 * 60 * 60
REGISTRY: dict[str, dict] = {}


def _listener_uid(port: int) -> int | None:
    """Return the owner of a loopback listening socket, if one exists."""
    for filename, loopbacks in (
        ("/proc/net/tcp", {"0100007F", "00000000"}),
        ("/proc/net/tcp6", {"00000000000000000000000000000001", "00000000000000000000000000000000"}),
    ):
        try:
            lines = Path(filename).read_text().splitlines()[1:]
        except OSError:
            continue
        for line in lines:
            fields = line.split()
            address, port_hex = fields[1].split(":")
            if int(port_hex, 16) == port and fields[3] == "0A" and address in loopbacks:
                return int(fields[7])
    return None


def _user_name(current_user) -> str | None:
    if isinstance(current_user, dict):
        return current_user.get("name")
    return getattr(current_user, "name", None)


def _valid(entry: dict) -> bool:
    if time.time() - entry["created"] > MAX_AGE:
        return False
    try:
        uid = pwd.getpwnam(entry["owner"]).pw_uid
    except KeyError:
        return False
    return _listener_uid(entry["port"]) == uid


class AuthenticatedHandler(HubOAuthenticated, web.RequestHandler):
    pass


class ClassroomOAuthCallbackHandler(HubOAuthCallbackHandler):
    """Complete standard Hub OAuth, then set the local session before redirect."""

    async def get(self):
        error = self.get_argument("error", False)
        if error:
            raise web.HTTPError(
                400, self.get_argument("error_description", error)
            )
        code = self.get_argument("code", False)
        if not code:
            raise web.HTTPError(400, "OAuth callback made without a token")
        state = self.get_argument("state", None)
        if state is None:
            raise web.HTTPError(400, "OAuth state is missing. Try logging in again.")
        cookie_name = self.hub_auth.get_state_cookie_name(state)
        cookie_state = self.get_secure_cookie(cookie_name)
        if cookie_state:
            self.hub_auth.clear_oauth_state_cookies(self)
        elif self.current_user:
            self.hub_auth.clear_oauth_state_cookies(self)
            self.redirect(self.hub_auth.get_next_url(state))
            return
        if isinstance(cookie_state, bytes):
            cookie_state = cookie_state.decode("ascii", "replace")
        if state != cookie_state:
            raise web.HTTPError(403, "OAuth state does not match. Try logging in again.")
        next_url = self.hub_auth.get_next_url(cookie_state)
        self.hub_auth.clear_oauth_state(cookie_state)
        self.hub_auth.clear_oauth_state_cookies(self)
        token = await self.hub_auth.token_for_code(code, sync=False)
        session_id = self.hub_auth.get_session_id(self)
        user = await self.hub_auth.user_for_token(
            token, session_id=session_id, sync=False
        )
        if user is None:
            raise web.HTTPError(500, "OAuth callback failed to identify a user")
        self.hub_auth.set_cookie(self, token)
        self.set_secure_cookie(
            CLASSROOM_COOKIE,
            "authenticated",
            path=SERVICE_PREFIX,
            secure=True,
            httponly=True,
            samesite="Lax",
            expires_days=0.5,
        )
        self.redirect(next_url or self.hub_auth.base_url)


class ClassroomHandler(HubOAuthenticated, web.RequestHandler):
    """Authenticate app assets with the service-local signed session."""

    def get_current_user(self):
        value = self.get_secure_cookie(CLASSROOM_COOKIE)
        if not value:
            return None
        return {"authenticated": True}


class RegisterHandler(AuthenticatedHandler):
    @web.authenticated
    def post(self):
        owner = _user_name(self.current_user)
        try:
            payload = json.loads(self.request.body or b"{}")
            port = int(payload["port"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            raise web.HTTPError(400, "A valid app port is required")
        if not owner:
            raise web.HTTPError(403)
        try:
            expected_uid = pwd.getpwnam(owner).pw_uid
        except KeyError:
            raise web.HTTPError(403)
        if not (1024 <= port <= 65535) or _listener_uid(port) != expected_uid:
            raise web.HTTPError(403, "The app port is not owned by this account")
        token = secrets.token_urlsafe(24)
        REGISTRY[token] = {"owner": owner, "port": port, "created": time.time()}
        self.set_header("Content-Type", "application/json")
        self.write({"token": token, "path": f"{SERVICE_PREFIX}s/{token}/"})


class UnregisterHandler(AuthenticatedHandler):
    @web.authenticated
    def delete(self, token: str):
        owner = _user_name(self.current_user)
        entry = REGISTRY.get(token)
        if entry and entry["owner"] == owner:
            REGISTRY.pop(token, None)
        self.set_status(204)


class ShareHandler(ClassroomHandler):
    @web.authenticated
    def _serve(self, token: str, remainder: str = ""):
        entry = REGISTRY.get(token)
        if not entry or not _valid(entry):
            REGISTRY.pop(token, None)
            raise web.HTTPError(404, "This app is no longer running")
        # nginx treats this location as internal, so ports cannot be selected by
        # an external URL. It preserves HTTP streaming and WebSocket upgrades.
        safe_path = remainder.lstrip("/").replace("\r", "").replace("\n", "")
        self.set_header(
            "X-Accel-Redirect",
            f"/__mansci_app_share/{token}/{entry['port']}/{safe_path}",
        )
        self.set_status(200)

    get = _serve
    post = _serve
    put = _serve
    patch = _serve
    delete = _serve
    options = _serve
    head = _serve


def _clean():
    for token, entry in list(REGISTRY.items()):
        if not _valid(entry):
            REGISTRY.pop(token, None)


def main():
    prefix = re.escape(SERVICE_PREFIX.rstrip("/"))
    app = web.Application([
        (r"/api/register", RegisterHandler),
        (r"/api/share/([^/]+)", UnregisterHandler),
        (prefix + r"/oauth_callback", ClassroomOAuthCallbackHandler),
        (prefix + r"/s/([^/]+)/(.*)", ShareHandler),
    ], cookie_secret=secrets.token_bytes(32))
    app.listen(LISTEN_PORT, address="127.0.0.1")
    PeriodicCallback(_clean, 60_000).start()
    IOLoop.current().start()


if __name__ == "__main__":
    main()
