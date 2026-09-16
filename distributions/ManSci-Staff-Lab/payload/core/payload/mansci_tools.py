"""Student-friendly runners for the managed ManSci Python environments."""
from __future__ import annotations

import atexit
import importlib.util
import os
from pathlib import Path
import runpy
import socket
import subprocess
import sys
import tempfile
import time
from urllib.parse import quote

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


def _display_link(url: str, path: Path, kind: str) -> None:
    try:
        from IPython.display import HTML, display
        label = f"Open {kind.title()} app: {path.name}"
        display(HTML(f'<p><a href="{quote(url, safe=":/?=&%")}" target="_blank"><strong>{label}</strong></a></p>'))
    except Exception:
        print("Open:", url)


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
    if kind == "streamlit":
        command = [sys.executable, "-m", "streamlit", "run", path.name,
                   "--server.address", "127.0.0.1", "--server.port", str(app_port),
                   "--server.headless", "true", "--browser.gatherUsageStats", "false"]
    else:
        command = [sys.executable, path.name]
    log_dir = Path(tempfile.gettempdir()) / "mansci-app-logs"
    log_dir.mkdir(parents=True, exist_ok=True)
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
                print(f"Started {kind} from {path.parent}")
                _display_link(url, path, kind)
                print(f"Stop it later with: stop_app({path.name!r})")
                return {"file": str(path), "kind": kind, "port": app_port, "url": url,
                        "pid": process.pid, "log": str(log_path)}
        except OSError:
            time.sleep(.2)
    if process.poll() is not None:
        tail = log_path.read_text(encoding="utf-8", errors="replace")[-4000:]
        _PROCESSES.pop(key, None)
        raise RuntimeError(f"The app stopped during startup.\n\n{tail}")
    url = _url(app_port)
    print(f"The process is still starting. Log: {log_path}")
    _display_link(url, path, kind)
    return {"file": str(path), "kind": kind, "port": app_port, "url": url,
            "pid": process.pid, "log": str(log_path)}


def stop_app(file_path: str | os.PathLike | None = None) -> int:
    """Stop one app, or all apps started by this notebook kernel."""
    keys = list(_PROCESSES) if file_path is None else [str(resolve_path(file_path))]
    stopped = 0
    for key in keys:
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
