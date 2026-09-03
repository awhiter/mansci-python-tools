#!/bin/bash
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
VERSION="2026.09.03.1"
echo "ManSci Python Core Installer"
echo "============================"
case "$(uname -m)" in arm64) echo "Mac detected: Apple silicon";; x86_64) echo "Mac detected: Intel";; *) echo "WARNING: Unrecognised Mac architecture: $(uname -m)";; esac
CONDA_EXE=""
for candidate in "$HOME/miniconda3/bin/conda" /opt/miniconda3/bin/conda "$HOME/anaconda3/bin/conda" /opt/anaconda3/bin/conda /opt/homebrew/Caskroom/miniconda/base/bin/conda /usr/local/Caskroom/miniconda/base/bin/conda; do
  if [ -x "$candidate" ]; then CONDA_EXE="$candidate"; break; fi
done
if [ -z "$CONDA_EXE" ]; then CONDA_EXE="$(command -v conda 2>/dev/null || true)"; fi
if [ -z "$CONDA_EXE" ]; then
  echo "ERROR: Miniconda was not found. Install the correct Apple silicon or Intel installer from:"
  echo "https://docs.conda.io/projects/miniconda/en/latest/"
  [ "${MANSCI_EMBEDDED:-0}" = 1 ] || read -r -p "Press Return to close..."
  exit 1
fi
mkdir -p "$HOME/Library/Application Support/ManagementScience/Core"
printf '%s\n' "$CONDA_EXE" > "$HOME/Library/Application Support/ManagementScience/Core/conda-path.txt"
if "$CONDA_EXE" env list | awk '{print $1}' | grep -qx mansci-python; then
  "$CONDA_EXE" env update -n mansci-python -f "$ROOT/payload/environment.yml" || exit 1
else
  "$CONDA_EXE" env create -f "$ROOT/payload/environment.yml" || exit 1
fi
"$CONDA_EXE" run --no-capture-output -n mansci-python python "$ROOT/payload/core_setup.py" initialise || exit 1
OLLAMA="$(command -v ollama 2>/dev/null || true)"
if [ -z "$OLLAMA" ] && [ -x /Applications/Ollama.app/Contents/Resources/ollama ]; then OLLAMA=/Applications/Ollama.app/Contents/Resources/ollama; fi
if [ -z "$OLLAMA" ] && command -v brew >/dev/null 2>&1; then
  echo "Ollama is missing; installing it with Homebrew..."
  brew install --cask ollama || true
  [ -x /Applications/Ollama.app/Contents/Resources/ollama ] && OLLAMA=/Applications/Ollama.app/Contents/Resources/ollama
fi
if [ -n "$OLLAMA" ]; then
  ("$OLLAMA" serve >/dev/null 2>&1 &) || true
  sleep 2
  "$OLLAMA" pull qwen2.5-coder:3b || echo "WARNING: Qwen download failed; rerun this installer later."
else
  echo "Ollama could not be installed automatically. Install it from https://ollama.com/download and rerun Core."
fi
echo "Core $VERSION installation complete."
[ "${MANSCI_EMBEDDED:-0}" = 1 ] || read -r -p "Press Return to close..."
