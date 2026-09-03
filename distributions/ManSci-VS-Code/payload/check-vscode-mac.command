#!/bin/bash
set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
. "$SCRIPT_DIR/macos-common.sh"
find_conda || { read -r -p "Press Return to close..."; exit 1; }
find_vscode || { read -r -p "Press Return to close..."; exit 1; }
ensure_ollama_running || true
support_dir="$HOME/Library/Application Support/ManagementScienceVSCode"
MANSCI_VSCODE_SUPPORT="$support_dir" "$CONDA_EXE" run --no-capture-output -n mansci-python python "$SCRIPT_DIR/vscode_setup.py" status --conda "$CONDA_EXE" --code "$CODE_EXE" --source "$SCRIPT_DIR"
status=$?
echo
read -r -p "Press Return to close..."
exit "$status"
