"""Student-friendly runners for the managed ManSci Python environments."""
from __future__ import annotations

import atexit
import base64
from html import escape
import importlib.util
from io import BytesIO
import os
from pathlib import Path
import runpy
import socket
import subprocess
import sys
import tempfile
import time
from urllib.parse import quote
from urllib.request import Request, urlopen

__all__ = ["resolve_path", "run_script", "run_app", "stop_app", "app_status"]

APP_MODULES = {
    "streamlit": "streamlit",
    "gradio": "gradio",
    "dash": "dash",
    "flask": "flask",
    "python": None,
}

_PROCESSES: dict[str, subprocess.Popen] = {}
_LOGS: dict[str, Path] = {}
_SHARES: dict[str, str] = {}


def _roots() -> list[Path]:
    roots: list[Path] = []
    vm = Path.home() / "notebooks"
    if vm.is_dir():
        roots.append(vm)
    pointer = Path.home() / "Documents" / "ManSci Code Home.txt"
    if pointer.is_file():
        try:
            roots.append(Path(os.path.expandvars(pointer.read_text(encoding="utf-8").strip())).expanduser())
        except OSError:
            pass
    roots.append(Path.home() / "Documents" / "ManSci Code")
    roots.append(Path.cwd())
    unique = []
    for root in roots:
        root = root.resolve()
        if root not in unique and root.exists():
            unique.append(root)
    return unique


def resolve_path(file_path: str | os.PathLike) -> Path:
    """Resolve a student path against the VM or local ManSci workspace."""
    raw = str(file_path).strip()
    if not raw:
        raise ValueError("Enter a file path, for example 'party.py'.")
    expanded = Path(os.path.expandvars(raw)).expanduser()
    candidates = [expanded] if expanded.is_absolute() else [Path.cwd() / expanded]
    relative = raw.replace("\\", "/")
    if relative.startswith("~/notebooks/"):
        relative = relative[len("~/notebooks/"):]
    elif relative in {"~/notebooks", "notebooks", "/notebooks"}:
        relative = "."
    elif relative.startswith("notebooks/"):
        relative = relative[len("notebooks/"):]
    elif relative.startswith("/"):
        relative = relative[1:]
    for root in _roots():
        candidates.append(root / relative)
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
            if resolved.exists():
                return resolved
        except OSError:
            continue
    if "/" not in relative and "\\" not in raw:
        matches = []
        for root in _roots():
            try:
                matches.extend(p for p in root.rglob(relative) if p.is_file())
            except OSError:
                pass
        matches = list(dict.fromkeys(p.resolve() for p in matches))
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            choices = "\n".join(f"- {p}" for p in matches[:10])
            raise FileNotFoundError(f"More than one file is named {relative}. Use one of these paths:\n{choices}")
    raise FileNotFoundError(f"Could not find {file_path!r} in the ManSci workspace. Save the file first and check its name.")


def run_script(file_path: str | os.PathLike):
    """Run an ordinary Python script from its own project folder."""
    path = resolve_path(file_path)
    if path.suffix.lower() != ".py":
        raise ValueError("run_script expects a saved .py file.")
    old = Path.cwd()
    try:
        os.chdir(path.parent)
        return runpy.run_path(str(path), run_name="__main__")
    finally:
        os.chdir(old)


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _url(port: int) -> str:
    prefix = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "")
    if prefix:
        return f"{prefix.rstrip('/')}/proxy/{port}/"
    # Jupyter Server Proxy is installed in ManSci Lab and serves this relative route.
    return f"/proxy/{port}/"


def _phone_url(url: str) -> str | None:
    """Return a VM login URL that preserves the app route after authentication."""
    if not os.environ.get("JUPYTERHUB_SERVICE_PREFIX"):
        return None
    base = os.environ.get("MANSCI_PUBLIC_BASE_URL", "").strip().rstrip("/")
    if not base.startswith("https://"):
        return None
    # A phone usually has no existing Hub session. Linking straight to the
    # single-user proxy starts its OAuth flow, which can lose the original app
    # route and leave a newly authenticated user at JupyterLab. Enter through
    # the Hub login handler and carry the proxy route explicitly as ``next``.
    return f"{base}/hub/login?next={quote(url, safe='')}"


def _share_request(path: str, *, method: str = "GET", data: dict | None = None) -> dict | None:
    """Call the VM-only sharing service as the current JupyterHub user."""
    api_token = os.environ.get("JUPYTERHUB_API_TOKEN", "")
    if not os.environ.get("JUPYTERHUB_SERVICE_PREFIX") or not api_token:
        return None
    body = None if data is None else __import__("json").dumps(data).encode("utf-8")
    request = Request(
        "http://127.0.0.1:8999" + path,
        data=body,
        method=method,
        headers={"Authorization": f"token {api_token}", "Content-Type": "application/json"},
    )
    with urlopen(request, timeout=4) as response:
        raw = response.read()
    return __import__("json").loads(raw) if raw else {}


def _register_share(port: int) -> tuple[str | None, str | None]:
    try:
        result = _share_request("/api/register", method="POST", data={"port": port})
        if result and result.get("token") and result.get("path"):
            return str(result["token"]), str(result["path"])
    except Exception as exc:
        print(f"Classroom phone sharing is temporarily unavailable: {exc}")
    return None, None


def _unregister_share(token: str) -> None:
    try:
        _share_request(f"/api/share/{quote(token, safe='')}", method="DELETE")
    except Exception:
        pass


def _qr_data_uri(url: str) -> str:
    import qrcode
    image = qrcode.make(url)
    data = BytesIO()
    image.save(data, format="PNG")
    return "data:image/png;base64," + base64.b64encode(data.getvalue()).decode("ascii")


def _display_link(
    url: str,
    path: Path,
    kind: str,
    phone_url: str | None = None,
    classroom_shared: bool = False,
) -> None:
    try:
        from IPython.display import HTML, display
        label = f"Open {kind.title()} app: {path.name}"
        parts = [
            '<div style="border:1px solid #d9d9d9;border-radius:8px;padding:14px;max-width:680px">',
            f'<p style="margin-top:0"><a href="{quote(url, safe=":/?=&%")}" target="_blank"><strong>{escape(label)}</strong></a></p>',
        ]
        if phone_url:
            safe_phone_url = escape(phone_url, quote=True)
            heading = "Share with the class" if classroom_shared else "Open on your phone"
            guidance = (
                "Anyone with an account on this ManSci VM can scan this code and sign in with "
                "their own account."
                if classroom_shared else
                "Scan this code, then sign into the ManSci VM with your own account if asked."
            )
            try:
                qr = _qr_data_uri(phone_url)
                parts.append(
                    f'<div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap">'
                    f'<img src="{qr}" alt="QR code for the authenticated phone preview" '
                    f'style="width:180px;height:180px;image-rendering:pixelated">'
                    f'<div><strong>{heading}</strong><p>{guidance}</p><p><a href="{safe_phone_url}" target="_blank">'
                    f'{safe_phone_url}</a></p><p>The link contains no password or access token. The app remains '
                    f'available only while your VM server and this app process are running.</p></div></div>'
                )
            except Exception:
                parts.append(
                    f'<p><strong>Open on your phone:</strong> <a href="{safe_phone_url}" target="_blank">'
                    f'{safe_phone_url}</a></p><p>Sign into the ManSci VM with your own account if asked.</p>'
                )
        parts.append('</div>')
        display(HTML("".join(parts)))
    except Exception:
        print("Open:", url)
        if phone_url:
            print("Open on your phone:", phone_url)
            print("Sign into the ManSci VM with your own account if asked.")


def _app_command(path: Path, kind: str, port: int) -> list[str]:
    """Build the managed launch command for a supported application type."""
    if kind == "streamlit":
        return [sys.executable, "-m", "streamlit", "run", path.name,
                "--server.address", "127.0.0.1", "--server.port", str(port),
                "--server.headless", "true", "--browser.gatherUsageStats", "false"]
    if kind == "flask":
        # The Flask CLI supplies our port even when a student script contains a
        # conventional ``app.run(debug=True)`` under its __main__ guard.
        return [sys.executable, "-m", "flask", "--app", path.name, "run",
                "--host", "127.0.0.1", "--port", str(port),
                "--no-debugger", "--no-reload"]
    return [sys.executable, path.name]


def run_app(file_path: str | os.PathLike, kind: str = "streamlit", *, port: int | None = None):
    """Start a saved app from its project folder and show its proxied link.

    Supported kinds are streamlit, gradio, dash, flask and python. For non-Streamlit
    server scripts, generated code should read MANSCI_APP_PORT (or PORT) and bind to
    127.0.0.1. Use stop_app() before starting a substantially different app.
    """
    path = resolve_path(file_path)
    if path.suffix.lower() != ".py":
        raise ValueError("run_app expects a saved .py file.")
    kind = kind.lower().strip()
    if kind not in APP_MODULES:
        raise ValueError("kind must be streamlit, gradio, dash, flask or python.")
    required_module = APP_MODULES[kind]
    if required_module and importlib.util.find_spec(required_module) is None:
        raise ModuleNotFoundError(
            f"{kind.title()} is not installed in this Python environment. "
            "Use the Management Science Python kernel or contact the teaching team."
        )
    stop_app(path)
    app_port = int(port or _free_port())
    env = dict(os.environ, MANSCI_APP_PORT=str(app_port), PORT=str(app_port),
               GRADIO_SERVER_PORT=str(app_port), GRADIO_SERVER_NAME="127.0.0.1")
    command = _app_command(path, kind, app_port)
    # A shared fixed folder lets the first VM user prevent other accounts from
    # writing logs. Keep each user's app logs private and independently writable.
    user_id = os.getuid() if hasattr(os, "getuid") else os.getpid()
    log_dir = Path(tempfile.gettempdir()) / f"mansci-app-logs-{user_id}"
    log_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    log_path = log_dir / f"{path.stem}-{app_port}.log"
    log = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(command, cwd=path.parent, env=env, stdin=subprocess.DEVNULL,
                               stdout=log, stderr=subprocess.STDOUT)
    log.close()
    key = str(path)
    _PROCESSES[key] = process
    _LOGS[key] = log_path
    deadline = time.time() + 12
    while time.time() < deadline and process.poll() is None:
        try:
            with socket.create_connection(("127.0.0.1", app_port), timeout=.25):
                url = _url(app_port)
                share_token, share_path = _register_share(app_port)
                phone_url = _phone_url(share_path or url)
                if share_token:
                    _SHARES[key] = share_token
                print(f"Started {kind} from {path.parent}")
                _display_link(url, path, kind, phone_url, classroom_shared=bool(share_token))
                print(
                    "Stop it later with: "
                    f"from mansci_tools import stop_app; stop_app({path.name!r})"
                )
                return {"file": str(path), "kind": kind, "port": app_port, "url": url,
                        "phone_url": phone_url, "shared_with_vm_accounts": bool(share_token),
                        "pid": process.pid, "log": str(log_path)}
        except OSError:
            time.sleep(.2)
    if process.poll() is not None:
        tail = log_path.read_text(encoding="utf-8", errors="replace")[-4000:]
        _PROCESSES.pop(key, None)
        raise RuntimeError(f"The app stopped during startup.\n\n{tail}")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
    _PROCESSES.pop(key, None)
    tail = log_path.read_text(encoding="utf-8", errors="replace")[-4000:]
    raise RuntimeError(
        f"The {kind} app did not open its assigned port {app_port}, so no app link "
        f"was created. Check that the file starts a {kind} application.\n"
        f"Log: {log_path}\n\n{tail}"
    )


def stop_app(file_path: str | os.PathLike | None = None) -> int:
    """Stop one app, or all apps started by this notebook kernel."""
    keys = list(_PROCESSES) if file_path is None else [str(resolve_path(file_path))]
    stopped = 0
    for key in keys:
        share_token = _SHARES.pop(key, None)
        if share_token:
            _unregister_share(share_token)
        process = _PROCESSES.pop(key, None)
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            stopped += 1
    if stopped:
        print(f"Stopped {stopped} app process{'es' if stopped != 1 else ''}.")
    return stopped


def app_status() -> list[dict]:
    """Return the apps started by this notebook kernel and their state."""
    result = []
    for key, process in list(_PROCESSES.items()):
        result.append({"file": key, "pid": process.pid, "running": process.poll() is None,
                       "log": str(_LOGS.get(key, ""))})
    return result


atexit.register(stop_app)
