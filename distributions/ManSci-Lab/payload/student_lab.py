#!/usr/bin/env python3
"""Launch the student ManSci Lab with its private kernel and local Qwen chat."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.parse import quote, urlsplit
from urllib.error import URLError
from urllib.request import urlopen


APP_NAME = "ManagementSciencePython"
LOCAL_MODEL = "qwen2.5-coder:3b"


def data_dir() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", Path.home())) / APP_NAME
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / APP_NAME


def documents_dir() -> Path:
    configured = os.environ.get("MANSCI_STUDENT_WORKSPACE")
    if configured:
        return Path(os.path.expandvars(configured)).expanduser()

    default = Path.home() / "Documents" / "ManSci Code"
    location_file = Path.home() / "Documents" / "ManSci Code Home.txt"
    try:
        if location_file.exists():
            saved = location_file.read_text(encoding="utf-8").strip()
            if saved:
                return Path(os.path.expandvars(saved)).expanduser()
        location_file.parent.mkdir(parents=True, exist_ok=True)
        location_file.write_text(str(default) + "\n", encoding="utf-8")
    except OSError:
        # A managed or protected Documents folder should not prevent startup.
        pass
    return default


def ollama_executable() -> str | None:
    found = shutil.which("ollama")
    if found:
        return found
    candidates: list[Path] = []
    if sys.platform == "darwin":
        candidates.append(Path("/Applications/Ollama.app/Contents/Resources/ollama"))
    elif os.name == "nt":
        local = Path(os.environ.get("LOCALAPPDATA", ""))
        candidates.extend(
            [local / "Programs" / "Ollama" / "ollama.exe", local / "Ollama" / "ollama.exe"]
        )
    return next((str(path) for path in candidates if path.is_file()), None)


def ollama_ready() -> bool:
    try:
        with urlopen("http://127.0.0.1:11434/api/tags", timeout=1) as response:
            return response.status == 200
    except (URLError, TimeoutError, OSError):
        return False


def start_ollama() -> bool:
    if ollama_ready():
        return True
    executable = ollama_executable()
    if not executable:
        return False
    kwargs: dict = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL,
                    "env": dict(os.environ, OLLAMA_HOST='127.0.0.1:11434')}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
    subprocess.Popen([executable, "serve"], **kwargs)
    for _ in range(20):
        if ollama_ready():
            return True
        time.sleep(0.5)
    return False


def local_model_installed(executable: str) -> bool:
    result = subprocess.run([executable, "list"], capture_output=True, text=True, check=False)
    return result.returncode == 0 and any(
        line.split()[0].split(":latest")[0] in {LOCAL_MODEL, LOCAL_MODEL.split(":")[0]}
        for line in result.stdout.splitlines()[1:]
        if line.split()
    )


def setup_local_model() -> None:
    executable = ollama_executable()
    if not executable:
        raise RuntimeError(
            "Ollama is not installed. Install it from https://ollama.com/download, then retry."
        )
    if not start_ollama():
        raise RuntimeError("Ollama was found but its local service did not start.")
    if local_model_installed(executable):
        print(f"Local model already installed: {LOCAL_MODEL}")
        return
    print(f"Downloading {LOCAL_MODEL} (approximately 2 GB)...")
    subprocess.run([executable, "pull", LOCAL_MODEL], check=True)
    print("Local model setup: PASS")


def write_private_kernelspec() -> None:
    target = data_dir() / "jupyter-data" / "kernels" / "mansci-python" / "kernel.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {
                "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
                "display_name": "Management Science Python",
                "language": "python",
                "metadata": {"debugger": True},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def install_local_persona(workspace: Path) -> None:
    source = Path(__file__).resolve().parent / "personas"
    target = workspace / ".jupyter" / "personas"
    target.mkdir(parents=True, exist_ok=True)
    for name in ("qwen_local_persona.py", "qwen-local.svg"):
        shutil.copy2(source / name, target / name)


def running_server_url(runtime: Path, workspace: Path) -> str | None:
    """Reopen this distribution's live server instead of starting a duplicate."""
    for server_file in sorted(runtime.glob("jpserver-*.json"), reverse=True):
        try:
            details = json.loads(server_file.read_text(encoding="utf-8"))
            if Path(details["root_dir"]).resolve() != workspace.resolve():
                continue
            base_url = str(details["url"]).rstrip("/")
            if urlsplit(base_url).hostname not in ('localhost', '127.0.0.1', '::1'):
                continue
            token = quote(str(details.get("token", "")), safe="")
            # os.kill(pid, 0) is NOT a safe process probe on Windows.
            # Check the authenticated local HTTP endpoint instead.
            with urlopen(f'{base_url}/api/status?token={token}', timeout=1) as response:
                if response.status != 200:
                    continue
            target = f"{base_url}/lab"
            if token:
                target += f"?token={token}"
            return target
        except (FileNotFoundError, KeyError, ValueError, TypeError, OSError, json.JSONDecodeError):
            continue
    return None


def open_existing_server(runtime: Path, workspace: Path) -> bool:
    """Legacy browser helper; managed launch uses the singleton desktop window."""
    target = running_server_url(runtime, workspace)
    if target:
        webbrowser.open(target)
        return True
    return False


def launch() -> int:
    from lab_window import run
    return run()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("launch", "setup-qwen"), nargs="?", default="launch")
    args = parser.parse_args()
    try:
        if args.action == "setup-qwen":
            setup_local_model()
            return 0
        return launch()
    except (RuntimeError, subprocess.CalledProcessError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
