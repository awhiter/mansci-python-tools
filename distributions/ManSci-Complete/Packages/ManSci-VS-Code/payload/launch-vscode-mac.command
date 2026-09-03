#!/bin/bash
set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
. "$SCRIPT_DIR/macos-common.sh"
find_conda || { if [ -t 0 ]; then read -r -p "Press Return to close..."; fi; exit 1; }
find_vscode || { if [ -t 0 ]; then read -r -p "Press Return to close..."; fi; exit 1; }
ensure_ollama_running || true
support_dir="$HOME/Library/Application Support/ManagementScienceVSCode"
MANSCI_VSCODE_SUPPORT="$support_dir" "$CONDA_EXE" run --no-capture-output -n mansci-python python "$SCRIPT_DIR/vscode_setup.py" launch --conda "$CONDA_EXE" --code "$CODE_EXE" --source "$SCRIPT_DIR"
status=$?
if [ "$status" -ne 0 ] && [ -t 0 ]; then read -r -p "ManSci VS Code failed to start. Press Return to close..."; fi
exit "$status"
