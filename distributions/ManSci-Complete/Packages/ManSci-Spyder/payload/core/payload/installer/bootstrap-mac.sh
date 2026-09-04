#!/bin/bash
set -euo pipefail
PACKAGE="$1"; KIND="$2"
LOGDIR="$HOME/Library/Logs/ManagementScience"
mkdir -p "$LOGDIR"
export MANSCI_INSTALL_LOG="$LOGDIR/install-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$MANSCI_INSTALL_LOG") 2>&1
fail() { echo "INSTALLATION NOT COMPLETE: $*"; echo "See README.md / DISTRIBUTION-GUIDE.md. Log: $MANSCI_INSTALL_LOG"; exit 1; }
agree() { local reply; read -r -p "$* [y/N] " reply; [[ "$reply" = y || "$reply" = Y || "$reply" = yes ]]; }
echo "Management Science $KIND installer - staff testing"
echo 'Stages: 1 prerequisites; 2 terms; 3 Python environment; 4 local AI; 5 tool launchers.'
echo 'Keep this window open. Downloads can take many minutes. Watch for consent prompts.'
echo 'If Ollama opens, choose LOCAL use, not sign in. No account is required. Its service starts automatically.'
echo 'Close all ManSci tools before continuing.'
echo "Log: $MANSCI_INSTALL_LOG"
agree 'Ready to check/install the required software?' || fail 'Cancelled.'
ARCH="$(uname -m)"
if [ "$(sysctl -in hw.optional.arm64 2>/dev/null || true)" = 1 ]; then ARCH=arm64; fi
case "$ARCH" in arm64|x86_64) ;; *) fail "Unsupported Mac architecture $ARCH";; esac
echo "[1/5] Checking all prerequisites. Mac architecture: $ARCH"
export MANSCI_CODE="" MANSCI_OLLAMA=""
find_code() { for p in '/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code' "$HOME/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"; do if [ -x "$p" ]; then MANSCI_CODE="$p"; return; fi; done; }
find_ollama() { MANSCI_OLLAMA="$(command -v ollama || true)"; for p in /Applications/Ollama.app/Contents/Resources/ollama "$HOME/Applications/Ollama.app/Contents/Resources/ollama"; do if [ -x "$p" ]; then MANSCI_OLLAMA="$p"; return; fi; done; }
if [ "$KIND" = Complete ] || [ "$KIND" = VS-Code ]; then
  find_code
  if [ -z "$MANSCI_CODE" ] && command -v brew >/dev/null && agree 'VS Code is missing. Install it using Homebrew?'; then brew install --cask visual-studio-code; find_code; fi
  [ -n "$MANSCI_CODE" ] || fail 'Install VS Code from https://code.visualstudio.com/download, move it to Applications, then rerun. No Python packages have been changed.'
fi
find_ollama
if [ -z "$MANSCI_OLLAMA" ] && command -v brew >/dev/null && agree 'Ollama is missing. Install it using Homebrew?'; then brew install --cask ollama; find_ollama; fi
[ -n "$MANSCI_OLLAMA" ] || fail 'Install Ollama from https://ollama.com/download, move it to Applications, then rerun. Choose LOCAL use if prompted. No Python packages have been changed.'
CONDA=""
SAVED="$HOME/Library/Application Support/ManagementScience/Core/conda-path.txt"
if [ -f "$SAVED" ]; then CONDA="$(cat "$SAVED")"; fi
if [ ! -x "$CONDA" ]; then
  for p in "${CONDA_EXE:-}" "$HOME/miniconda3/bin/conda" /opt/miniconda3/bin/conda "$HOME/anaconda3/bin/conda" /opt/anaconda3/bin/conda /opt/homebrew/Caskroom/miniconda/base/bin/conda /usr/local/Caskroom/miniconda/base/bin/conda; do
    if [ -x "$p" ]; then CONDA="$p"; break; fi
  done
fi
if [ ! -x "$CONDA" ]; then CONDA="$(command -v conda || true)"; fi
if [ ! -x "$CONDA" ]; then
  read -r -p 'Conda not found. Enter an existing Conda folder, or press Return for automatic Miniconda installation: ' CUSTOM
  if [ -n "$CUSTOM" ]; then CONDA="$CUSTOM/bin/conda"; [ -x "$CONDA" ] || fail 'No bin/conda found in that folder.'; fi
fi
if [ ! -x "$CONDA" ]; then
  echo 'Miniconda terms: https://www.anaconda.com/legal'
  agree 'After reviewing the terms, do you agree and want Miniconda installed for this user?' || fail 'Miniconda consent declined.'
  [ ! -e "$HOME/miniconda3" ] || fail 'miniconda3 already exists but is not usable. It will not be overwritten; contact staff.'
  DOWNLOAD_DIR="$(mktemp -d)"
  echo 'Downloading Miniconda from Anaconda. Download and setup may take several minutes.'
  curl --fail --location --retry 3 "https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-$ARCH.sh" -o "$DOWNLOAD_DIR/miniconda.sh"
  bash "$DOWNLOAD_DIR/miniconda.sh" -b -p "$HOME/miniconda3"
  CONDA="$HOME/miniconda3/bin/conda"
fi
PYTHON="$(dirname "$CONDA")/python"
[ -x "$PYTHON" ] || fail 'Cannot find the Python belonging to this Conda installation.'
"$PYTHON" -u "$(dirname "$0")/install.py" --package "$PACKAGE" --kind "$KIND" --conda "$CONDA"
