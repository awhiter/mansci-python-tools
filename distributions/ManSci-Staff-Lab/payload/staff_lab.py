#!/usr/bin/env python3
"""Configure and launch ManSci Staff Lab without storing an Azure key in files."""

from __future__ import annotations

import argparse
import datetime as dt
import getpass
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

import keyring
from keyring.errors import KeyringError


APP_NAME = "ManSci Staff Lab"
KEYRING_SERVICE = "ManSci Staff Lab - Azure OpenAI"
KEYRING_ACCOUNT = "azure-openai-api-key"
DEFAULT_API_VERSION = "2024-10-21"
LOCAL_MODEL = "qwen2.5-coder:3b"


def data_dir() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME
    if os.name == "nt":
        return Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / APP_NAME


def documents_dir() -> Path:
    configured = os.environ.get("MANSCI_STAFF_WORKSPACE")
    if configured:
        return Path(os.path.expandvars(configured)).expanduser()
    default = Path.home() / "Documents" / "ManSci Code"
    pointer = Path.home() / "Documents" / "ManSci Code Home.txt"
    try:
        if pointer.exists():
            saved = pointer.read_text(encoding="utf-8").strip()
            if saved:
                return Path(os.path.expandvars(saved)).expanduser()
        pointer.parent.mkdir(parents=True, exist_ok=True)
        pointer.write_text(str(default) + "\n", encoding="utf-8")
    except OSError:
        pass
    return default


def settings_path() -> Path:
    return data_dir() / "settings.json"


def load_settings() -> dict[str, str]:
    try:
        value = json.loads(settings_path().read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def save_settings(settings: dict[str, str]) -> None:
    path = settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass


def normalise_endpoint(value: str) -> str:
    value = value.strip().rstrip("/")
    marker = "/openai/deployments/"
    if marker in value:
        value = value.split(marker, 1)[0]
    if not value.startswith("https://"):
        raise ValueError("The endpoint must begin with https://")
    return value


def read_key() -> str | None:
    try:
        return keyring.get_password(KEYRING_SERVICE, KEYRING_ACCOUNT)
    except KeyringError as exc:
        raise RuntimeError(f"The operating-system credential store could not be read: {exc}") from exc


def store_key(value: str) -> None:
    try:
        keyring.set_password(KEYRING_SERVICE, KEYRING_ACCOUNT, value)
    except KeyringError as exc:
        raise RuntimeError(
            "The operating-system credential store could not save the key. "
            "The key has not been written to a file."
        ) from exc


def delete_key() -> None:
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_ACCOUNT)
    except keyring.errors.PasswordDeleteError:
        pass
    except KeyringError as exc:
        raise RuntimeError(f"The credential could not be removed: {exc}") from exc


def prompt_settings(existing: dict[str, str] | None = None) -> tuple[dict[str, str], str]:
    existing = existing or {}
    print("Azure OpenAI setup")
    print("------------------")
    print("The key will be stored in your operating system's secure credential store.")
    endpoint_default = existing.get("endpoint", "")
    deployment_default = existing.get("deployment", "gpt-4.1")
    version_default = existing.get("api_version", DEFAULT_API_VERSION)

    endpoint_label = f"Azure endpoint [{endpoint_default}]: " if endpoint_default else "Azure endpoint: "
    endpoint = input(endpoint_label).strip() or endpoint_default
    deployment = input(f"Deployment name [{deployment_default}]: ").strip() or deployment_default
    api_version = input(f"API version [{version_default}]: ").strip() or version_default
    api_key = getpass.getpass("Azure OpenAI key (hidden): ").strip()

    if not api_key:
        raise ValueError("A key is required.")
    if not deployment:
        raise ValueError("A deployment name is required.")
    return {
        "endpoint": normalise_endpoint(endpoint),
        "deployment": deployment,
        "api_version": api_version,
    }, api_key


def test_azure(settings: dict[str, str], api_key: str) -> None:
    from openai import AzureOpenAI

    print("Testing the Azure deployment with a small request...")
    client = AzureOpenAI(
        api_key=api_key,
        azure_endpoint=settings["endpoint"],
        api_version=settings["api_version"],
    )
    result = client.chat.completions.create(
        model=settings["deployment"],
        messages=[{"role": "user", "content": "Reply with the single word READY."}],
        max_tokens=8,
    )
    if not result.choices:
        raise RuntimeError("Azure returned no response choices.")
    print("Azure connection: PASS")


def configure(force: bool = False) -> tuple[dict[str, str], str]:
    settings = load_settings()
    api_key = read_key()
    required = {"endpoint", "deployment", "api_version"}
    if force or not required.issubset(settings) or not api_key:
        new_settings, new_key = prompt_settings(settings)
        test_azure(new_settings, new_key)
        store_key(new_key)
        save_settings(new_settings)
        return new_settings, new_key
    return settings, api_key


def ollama_executable() -> str | None:
    found = shutil.which("ollama")
    if found:
        return found
    candidates = []
    if sys.platform == "darwin":
        candidates.append("/Applications/Ollama.app/Contents/Resources/ollama")
    elif os.name == "nt":
        local = Path(os.environ.get("LOCALAPPDATA", ""))
        candidates.extend(
            [str(local / "Programs" / "Ollama" / "ollama.exe"), str(local / "Ollama" / "ollama.exe")]
        )
    return next((path for path in candidates if Path(path).is_file()), None)


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
    kwargs: dict = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
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
            "Ollama is not installed. Install it from https://ollama.com/download, "
            "then run this setup again."
        )
    if not start_ollama():
        raise RuntimeError("Ollama was found but its local service did not start.")
    if local_model_installed(executable):
        print(f"Local model already installed: {LOCAL_MODEL}")
        return
    print(f"Downloading {LOCAL_MODEL} (approximately 2 GB)...")
    subprocess.run([executable, "pull", LOCAL_MODEL], check=True)
    print("Local model setup: PASS")


def write_jupyter_ai_config(settings: dict[str, str]) -> None:
    gid = f"azure/{settings['deployment']}"
    config = {
        "model_provider_id": gid,
        # LiteLLM's static catalogue does not necessarily contain tags served
        # by the user's local Ollama instance. Register Qwen explicitly so it
        # always appears at the top of Jupyternaut's model picker.
        "custom_models": [
            {
                "id": "custom-mansci-qwen/ollama/qwen2.5-coder:3b",
                "name": "Qwen2.5-Coder 3B (Local)",
                "description": "Runs locally through Ollama; no Azure usage or API key.",
                "model_id": f"ollama/{LOCAL_MODEL}",
                "params": {"api_base": "http://127.0.0.1:11434"},
            }
        ],
        "embeddings_provider_id": None,
        "completions_model_provider_id": None,
        "api_keys": {},
        "send_with_shift_enter": False,
        "fields": {
            gid: {
                "api_base": settings["endpoint"],
                "api_version": settings["api_version"],
            },
            f"ollama/{LOCAL_MODEL}": {"api_base": "http://127.0.0.1:11434"},
        },
        "embeddings_fields": {},
        "completions_fields": {},
    }
    target = data_dir() / "jupyter-data" / "jupyter_ai" / "config.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def write_private_kernelspec() -> None:
    """Expose this exact conda interpreter in Staff Lab's private data tree."""
    target = data_dir() / "jupyter-data" / "kernels" / "mansci-python" / "kernel.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    kernelspec = {
        "argv": [
            sys.executable,
            "-m",
            "ipykernel_launcher",
            "-f",
            "{connection_file}",
        ],
        "display_name": "Management Science Python",
        "language": "python",
        "metadata": {"debugger": True},
    }
    target.write_text(json.dumps(kernelspec, indent=2) + "\n", encoding="utf-8")


def install_local_persona(workspace: Path) -> None:
    """Install the ManSci and tool-free Qwen personas for Jupyter AI."""
    source = Path(__file__).resolve().parent / "personas"
    target = workspace / ".jupyter" / "personas"
    target.mkdir(parents=True, exist_ok=True)
    for pattern in ("*.py", "*.svg"):
        for item in source.glob(pattern):
            shutil.copy2(item, target / item.name)


def server_environment() -> dict[str, str]:
    settings, api_key = configure()
    write_jupyter_ai_config(settings)
    return {
            "AZURE_OPENAI_API_KEY": api_key,
            "AZURE_API_KEY": api_key,
            "AZURE_OPENAI_ENDPOINT": settings["endpoint"],
            "AZURE_API_BASE": settings["endpoint"],
            "OPENAI_API_VERSION": settings["api_version"],
            "AZURE_API_VERSION": settings["api_version"],
        }


def running_server_url(runtime: Path, workspace: Path) -> str | None:
    for server_file in sorted(runtime.glob("jpserver-*.json"), reverse=True):
        try:
            details = json.loads(server_file.read_text(encoding="utf-8"))
            if Path(details["root_dir"]).resolve() != workspace.resolve():
                continue
            base = str(details["url"]).rstrip("/")
            if urlsplit(base).hostname not in ("localhost", "127.0.0.1", "::1"):
                continue
            token = quote(str(details.get("token", "")), safe="")
            with urlopen(f"{base}/api/status?token={token}", timeout=1) as response:
                if response.status != 200:
                    continue
            return f"{base}/lab" + (f"?token={token}" if token else "")
        except (FileNotFoundError, KeyError, ValueError, TypeError, OSError, json.JSONDecodeError):
            continue
    return None


def stop_private_server() -> None:
    """Stop only Staff Lab servers authenticated by their private runtime file."""
    stopped = False
    for runtime in (data_dir() / "jupyter-runtime", data_dir() / "runtime"):
        for server_file in sorted(runtime.glob("jpserver-*.json")):
            try:
                details = json.loads(server_file.read_text(encoding="utf-8"))
                base = str(details["url"]).rstrip("/")
                if urlsplit(base).hostname not in ("localhost", "127.0.0.1", "::1"):
                    continue
                token = quote(str(details.get("token", "")), safe="")
                request = Request(f"{base}/api/shutdown?token={token}", method="POST")
                with urlopen(request, timeout=3) as response:
                    if response.status not in (200, 202):
                        continue
                stopped = True
            except (FileNotFoundError, KeyError, ValueError, TypeError, OSError, json.JSONDecodeError):
                continue
    if stopped:
        print("Previous ManSci Staff Lab server stopped so updated personas and configuration will load.")
        time.sleep(1)
    else:
        print("No running ManSci Staff Lab server needed to be stopped.")


def launch() -> int:
    from lab_window import run
    return run()


def status() -> None:
    settings = load_settings()
    print(f"Python: {sys.executable}")
    print(f"Conda environment: {os.environ.get('CONDA_DEFAULT_ENV', '(not reported)')}")
    print(f"Azure settings: {'PASS' if {'endpoint', 'deployment', 'api_version'}.issubset(settings) else 'NOT CONFIGURED'}")
    print(f"Secure Azure key: {'PASS' if read_key() else 'NOT CONFIGURED'}")
    print(f"Ollama: {'PASS' if ollama_executable() else 'NOT INSTALLED'}")
    print(f"Ollama service: {'PASS' if ollama_ready() else 'NOT RUNNING'}")


def repair_chat_memory() -> None:
    """Archive Jupyternaut checkpoints; visible .chat files are untouched."""
    source = data_dir() / "jupyter-data" / "jupyter_ai" / "memory.sqlite"
    if not source.exists():
        print("There is no persistent Jupyternaut checkpoint database to repair.")
        return
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    archive_dir = data_dir() / "checkpoint-archives" / stamp
    archive_dir.mkdir(parents=True, exist_ok=False)
    moved = []
    for suffix in ("", "-wal", "-shm"):
        candidate = Path(str(source) + suffix)
        if candidate.exists():
            target = archive_dir / candidate.name
            candidate.replace(target)
            moved.append(target.name)
    print(f"Archived Jupyternaut checkpoint database to: {archive_dir}")
    print("Visible notebooks and .chat files were not changed.")
    if moved:
        print("Archived files: " + ", ".join(moved))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=("launch", "configure", "ensure-configured", "stop-server", "forget-key", "setup-qwen", "repair-chat-memory", "status"),
        nargs="?",
        default="launch",
    )
    args = parser.parse_args()
    try:
        if args.action == "launch":
            return launch()
        if args.action == "configure":
            configure(force=True)
            print("Azure settings saved securely.")
        elif args.action == "ensure-configured":
            configure()
            print("Azure OpenAI staff configuration: PASS (key stored in the operating-system credential store).")
        elif args.action == "stop-server":
            stop_private_server()
        elif args.action == "forget-key":
            delete_key()
            print("The Azure key was removed from the operating-system credential store.")
        elif args.action == "setup-qwen":
            setup_local_model()
        elif args.action == "repair-chat-memory":
            repair_chat_memory()
        elif args.action == "status":
            status()
        return 0
    except (ValueError, RuntimeError, subprocess.CalledProcessError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
