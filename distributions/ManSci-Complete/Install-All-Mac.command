#!/bin/bash
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
echo "Management Science Complete Installer"
echo "======================================"
MANSCI_EMBEDDED=1 bash "$ROOT/Packages/ManSci-Core/Install-Mac.command" || exit 1
MANSCI_EMBEDDED=1 bash "$ROOT/Packages/ManSci-Spyder/Install-Mac.command" || exit 1
MANSCI_EMBEDDED=1 bash "$ROOT/Packages/ManSci-Lab/Install-Mac.command" || exit 1
MANSCI_EMBEDDED=1 bash "$ROOT/Packages/ManSci-VS-Code/Install-Mac.command" || exit 1
echo "All Management Science tools are installed."
read -r -p "Press Return to close..."
