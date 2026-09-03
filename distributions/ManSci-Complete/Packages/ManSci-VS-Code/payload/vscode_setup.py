#!/usr/bin/env python3
"""Configure, launch and diagnose the isolated ManSci VS Code environment."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path


APP_NAME = "ManagementScienceVSCode"
EXTENSIONS = (
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.debugpy",
    "ms-python.vscode-python-envs",
    "ms-toolsai.jupyter",
    "ms-python.black-formatter",
    "redhat.vscode-yaml",
    "continue.continue@1.2.11",
)

OBSOLETE_EXTENSIONS = ("ollama.ollama",)


def support_dir() -> Path:
    configured = os.environ.get("MANSCI_VSCODE_SUPPORT")
    if configured:
        return Path(configured).expanduser()
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", Path.home())) / APP_NAME
    return Path.home() / ".local" / "share" / APP_NAME


def workspace_dir() -> Path:
    configured = os.environ.get("MANSCI_VSCODE_WORKSPACE")
    if configured:
        return Path(os.path.expandvars(configured)).expanduser()
    default = Path.home() / "Documents" / "ManSci Code"
    setting = Path.home() / "Documents" / "ManSci Code Home.txt"
    try:
        if setting.exists():
            value = setting.read_text(encoding="utf-8").strip()
            if value:
                return Path(os.path.expandvars(value)).expanduser()
        setting.parent.mkdir(parents=True, exist_ok=True)
        setting.write_text(str(default) + "\n", encoding="utf-8")
    except OSError:
        pass
    return default


def settings(conda_executable: str) -> dict:
    envs_parent = str(Path(sys.prefix).parent)
    return {
        "python.defaultInterpreterPath": sys.executable,
        "python.condaPath": conda_executable,
        "python.useEnvironmentsExtension": True,
        "python.interpreter.infoVisibility": "always",
        "python-envs.defaultEnvManager": "ms-python.python:conda",
        "python-envs.defaultPackageManager": "ms-python.python:conda",
        "python-envs.globalSearchPaths": [envs_parent],
        "python-envs.terminal.autoActivationType": "command",
        "python.terminal.activateEnvironment": True,
        "python.terminal.executeInFileDir": True,
        "python.REPL.enableREPLSmartSend": True,
        "python.analysis.typeCheckingMode": "basic",
        "python.analysis.autoImportCompletions": True,
        "python.createEnvironment.trigger": "off",
        "jupyter.askForKernelRestart": False,
        "jupyter.alwaysTrustNotebooks": False,
        "jupyter.interactiveWindow.textEditor.autoMoveToNextCell": True,
        "jupyter.interactiveWindow.codeLens.enable": True,
        "jupyter.interactiveWindow.cellMarker.default": "# %%",
        "workbench.startupEditor": "none",
        "workbench.colorTheme": "Default Light+",
        "workbench.activityBar.location": "default",
        "workbench.sideBar.location": "left",
        "workbench.panel.defaultLocation": "bottom",
        "workbench.panel.opensMaximized": "never",
        "workbench.editor.showTabs": "multiple",
        "workbench.editor.enablePreview": False,
        "workbench.editor.openSideBySideDirection": "right",
        "workbench.tips.enabled": False,
        "window.commandCenter": False,
        "window.menuBarVisibility": "classic",
        "window.title": "ManSci VS Code — ${activeEditorShort}",
        "breadcrumbs.enabled": False,
        "editor.minimap.enabled": False,
        "editor.stickyScroll.enabled": False,
        "editor.codeLens": True,
        "editor.fontSize": 15,
        "editor.lineHeight": 23,
        "editor.wordWrap": "on",
        "editor.inlineSuggest.enabled": True,
        "explorer.openEditors.visible": 0,
        "explorer.compactFolders": False,
        "git.enabled": False,
        "scm.alwaysShowRepositories": False,
        "debug.toolBarLocation": "floating",
        "testing.openTesting": "neverOpen",
        "terminal.integrated.defaultLocation": "panel",
        "terminal.integrated.fontSize": 14,
        "notebook.lineNumbers": "on",
        "notebook.output.textLineLimit": 200,
        "security.workspace.trust.enabled": False,
        "telemetry.telemetryLevel": "off",
        "extensions.autoUpdate": False,
        "extensions.ignoreRecommendations": True,
        "chat.disableAIFeatures": True,
        "continue.telemetryEnabled": False,
        "continue.showInlineTip": False,
        "continue.enableTabAutocomplete": True,
        "continue.enableNextEdit": False,
        "[python]": {
            "editor.defaultFormatter": "ms-python.black-formatter",
            "editor.formatOnType": False,
            "editor.formatOnSave": False,
            "editor.rulers": [88],
        },
        "files.associations": {"*.py": "python"},
        "files.exclude": {
            "**/__pycache__": True,
            "**/.pytest_cache": True,
            "**/.git": True,
            "**/.DS_Store": True,
        },
    }


def notebook_template() -> dict:
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "id": "mansci-intro",
                "metadata": {},
                "source": [
                    "# Management Science notebook\n",
                    "\n",
                    "This notebook is configured to use **Management Science Python**.",
                ],
            },
            {
                "cell_type": "code",
                "id": "mansci-check",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": ["import sys\n", "print(sys.executable)"],
            },
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Management Science Python",
                "language": "python",
                "name": "mansci-python",
            },
            "language_info": {"name": "python", "version": platform.python_version()},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=4) + "\n", encoding="utf-8")


def configure_activity_bar(root: Path) -> None:
    """Keep the teaching views while unpinning Source Control and Testing."""
    viewlets = [
        {"id": "workbench.view.explorer", "pinned": True, "visible": True, "order": 0},
        {"id": "workbench.view.search", "pinned": True, "visible": False, "order": 1},
        {"id": "workbench.view.scm", "pinned": False, "visible": False, "order": 2},
        {"id": "workbench.view.debug", "pinned": True, "visible": False, "order": 3},
        {"id": "workbench.view.extensions", "pinned": True, "visible": False, "order": 4},
        {"id": "workbench.view.extension.test", "pinned": False, "visible": False, "order": 6},
        {"id": "workbench.view.extension.jupyter", "pinned": True, "visible": False, "order": 7},
        {"id": "workbench.view.extension.continue", "pinned": True, "visible": False, "order": 8},
        {"id": "workbench.view.extension.python", "pinned": True, "visible": False, "order": 9},
    ]
    db = root / "user-data" / "User" / "globalStorage" / "state.vscdb"
    db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db, timeout=10) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS ItemTable "
            "(key TEXT UNIQUE ON CONFLICT REPLACE, value BLOB)"
        )
        connection.execute(
            "INSERT OR REPLACE INTO ItemTable(key, value) VALUES(?, ?)",
            ("workbench.activity.pinnedViewlets2", json.dumps(viewlets)),
        )


def ensure_notebook_kernels(workspace: Path) -> None:
    """Assign Python notebooks in the teaching home to the ManSci kernel."""
    kernelspec = {
        "display_name": "Management Science Python",
        "language": "python",
        "name": "mansci-python",
    }
    for notebook in workspace.rglob("*.ipynb"):
        try:
            data = json.loads(notebook.read_text(encoding="utf-8"))
            if not isinstance(data.get("cells"), list):
                continue
            metadata = data.setdefault("metadata", {})
            language = metadata.get("language_info", {}).get("name", "python")
            if str(language).lower() != "python":
                continue
            if metadata.get("kernelspec") != kernelspec:
                metadata["kernelspec"] = kernelspec
                write_json(notebook, data)
        except (OSError, json.JSONDecodeError, AttributeError):
            continue


def continue_config() -> str:
    return """name: ManSci Local AI
version: 1.0.0
schema: v1

rules:
  - name: Management Science Python assistant
    alwaysApply: true
    rule: |
      You are assisting a Management Science student working in VS Code with
      Python 3.13 and the mansci-python Conda environment. Unless the user
      explicitly requests another language, interpret requests for code,
      functions, scripts, analysis or examples as requests for Python.

      Prefer clear, conventional, beginner-readable Python. Reuse the names,
      imports, data structures and style already present in the supplied file
      or selection. Before proposing a change, account for the selected code
      and all available surrounding code. Do not duplicate existing imports,
      functions or variables, and do not silently replace established inputs
      or outputs. Make the smallest complete change that satisfies the request.
      If essential context is unavailable, say what file, selection or
      definition should be added to context instead of inventing it.

      Generated code must be syntactically complete and suitable for the
      existing Python file or notebook. In chat, use a Python code block for
      code unless the interface requires code only. For an inline edit, return
      only the replacement code: no Markdown fences and no explanation.

models:
  - name: Qwen2.5-Coder 3B
    provider: ollama
    model: qwen2.5-coder:3b
    apiBase: http://127.0.0.1:11434
    roles:
      - chat
      - edit
      - apply
      - autocomplete
    defaultCompletionOptions:
      contextLength: 16384
      maxTokens: 2048
      temperature: 0.1
    autocompleteOptions:
      useImports: true
      useRecentlyEdited: true
      useRecentlyOpened: true
      experimental_includeRecentlyVisitedRanges: true
      experimental_includeRecentlyEditedRanges: true
    promptTemplates:
      edit: |
        You are editing a {{language}} file. Unless the request explicitly
        names another language, treat an unspecified coding request as Python.

        Code before the selected range:
        ```{{language}}
        {{{prefix}}}
        ```

        Selected code to replace:
        ```{{language}}
        {{{codeToEdit}}}
        ```

        Code after the selected range:
        ```{{language}}
        {{{suffix}}}
        ```

        User request: {{{userInput}}}

        Carefully preserve compatibility with the surrounding code, including
        existing imports, names, types, indentation, inputs and outputs. Make
        the smallest complete change. Do not duplicate definitions. Return
        only the exact replacement code for the selected range, with no
        Markdown fences and no explanation.
"""


def configure(conda_executable: str, source_dir: Path) -> None:
    root = support_dir()
    user_dir = root / "user-data" / "User"
    extensions_dir = root / "extensions"
    workspace = workspace_dir()
    workspace.mkdir(parents=True, exist_ok=True)
    extensions_dir.mkdir(parents=True, exist_ok=True)

    # Give the Jupyter extension one unambiguous kernelspec in the environment
    # inherited by VS Code. Notebook metadata names this same kernelspec.
    kernel_dir = root / "jupyter" / "kernels" / "mansci-python"
    write_json(
        kernel_dir / "kernel.json",
        {
            "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
            "display_name": "Management Science Python",
            "language": "python",
            "metadata": {"debugger": True},
        },
    )

    write_json(user_dir / "settings.json", settings(conda_executable))
    write_json(user_dir / "keybindings.json", [])
    obsolete_models = user_dir / "chatLanguageModels.json"
    if obsolete_models.exists():
        obsolete_models.unlink()
    continue_dir = root / "continue"
    continue_dir.mkdir(parents=True, exist_ok=True)
    (continue_dir / "config.yaml").write_text(continue_config(), encoding="utf-8")
    notebook = workspace / "New ManSci Notebook.ipynb"
    if not notebook.exists():
        write_json(notebook, notebook_template())
    ensure_notebook_kernels(workspace)

    for name in ("STUDENT-GUIDE.md", "student-profile-check.py"):
        source = source_dir / name
        target = workspace / name
        if source.is_file() and not target.exists():
            shutil.copy2(source, target)

    old_private_kernel = root / "jupyter" / "share" / "jupyter" / "kernels" / "mansci-python"
    if old_private_kernel.exists():
        shutil.rmtree(old_private_kernel)
    configure_activity_bar(root)
    manifest = {
        "python": sys.executable,
        "conda": conda_executable,
        "workspace": str(workspace),
        "user_data": str(root / "user-data"),
        "extensions": str(extensions_dir),
    }
    write_json(root / "installation.json", manifest)


def code_arguments(code_executable: str) -> list[str]:
    root = support_dir()
    return [
        code_executable,
        "--user-data-dir",
        str(root / "user-data"),
        "--extensions-dir",
        str(root / "extensions"),
    ]


def install_extensions(code_executable: str) -> None:
    listed_output = subprocess.run(
        code_arguments(code_executable) + ["--list-extensions", "--show-versions"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.lower().splitlines()
    installed: dict[str, str] = {}
    for line in listed_output:
        extension_id, separator, version = line.strip().partition("@")
        if extension_id:
            installed[extension_id] = version if separator else ""
    for extension in OBSOLETE_EXTENSIONS:
        if extension.lower() in installed:
            print(f"Removing superseded VS Code extension: {extension}")
            subprocess.run(
                code_arguments(code_executable) + ["--uninstall-extension", extension],
                check=True,
            )
    for extension in EXTENSIONS:
        extension_id, separator, required_version = extension.lower().partition("@")
        current_version = installed.get(extension_id)
        if current_version is not None and (
            not separator or current_version == required_version
        ):
            shown_version = f" {current_version}" if current_version else ""
            print(f"Already installed: {extension_id}{shown_version}")
            continue

        action = "Updating" if current_version is not None else "Installing"
        print(f"{action} VS Code extension: {extension}")
        command = code_arguments(code_executable) + ["--install-extension", extension]
        if current_version is not None:
            command.append("--force")
        for attempt in range(1, 4):
            completed = subprocess.run(command, check=False)
            if completed.returncode == 0:
                break
            if attempt == 3:
                raise RuntimeError(
                    f"Could not install {extension} after three attempts. "
                    "The VS Code Marketplace may be temporarily unavailable."
                )
            print(f"Download attempt {attempt} failed; retrying shortly...")
            time.sleep(3)
    configure_activity_bar(support_dir())


def launch(code_executable: str) -> None:
    root = support_dir()
    manifest_path = root / "installation.json"
    if not manifest_path.is_file():
        raise RuntimeError("The ManSci VS Code installation is incomplete. Rerun the installer.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    workspace = workspace_dir()
    workspace.mkdir(parents=True, exist_ok=True)
    ensure_notebook_kernels(workspace)
    env = os.environ.copy()
    env.update(
        {
            "MANSCI_PYTHON": str(manifest["python"]),
            "CONDA_EXE": str(manifest["conda"]),
            "CONTINUE_GLOBAL_DIR": str(root / "continue"),
            "JUPYTER_PATH": str(root / "jupyter"),
        }
    )
    kwargs: dict = {
        "env": env,
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(
        code_arguments(code_executable)
        + ["--new-window", "--disable-workspace-trust", str(workspace)],
        **kwargs,
    )


def status(code_executable: str) -> int:
    root = support_dir()
    expected = Path(sys.executable).resolve()
    checks = {
        "mansci-python interpreter": expected.parent.parent.name == "mansci-python",
        "VS Code command": Path(code_executable).exists(),
        "settings": (root / "user-data" / "User" / "settings.json").is_file(),
        "ipykernel in mansci-python": importlib.util.find_spec("ipykernel") is not None,
        "Continue local AI configuration": (root / "continue" / "config.yaml").is_file(),
        "Continue 1.2.11 extension": any(
            (root / "extensions").glob("continue.continue-1.2.11*")
        ),
        "workspace": workspace_dir().is_dir(),
    }
    print("Management Science VS Code - Installation Check")
    print("=" * 55)
    print(f"Python:    {sys.executable}")
    print(f"VS Code:   {code_executable}")
    print(f"Workspace: {workspace_dir()}")
    print()
    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    result = all(checks.values())
    print("=" * 55)
    print(f"OVERALL: {'PASS' if result else 'FAIL'}")
    return 0 if result else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("configure", "install-extensions", "launch", "status"))
    parser.add_argument("--conda", default=os.environ.get("CONDA_EXE", "conda"))
    parser.add_argument("--code", required=True)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    try:
        if args.action == "configure":
            configure(args.conda, args.source)
        elif args.action == "install-extensions":
            install_extensions(args.code)
        elif args.action == "launch":
            launch(args.code)
        else:
            return status(args.code)
        return 0
    except (OSError, RuntimeError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
