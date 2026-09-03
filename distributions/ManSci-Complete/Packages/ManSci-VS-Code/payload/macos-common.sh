#!/bin/bash

find_conda() {
  if [ -n "${CONDA_EXE:-}" ] && [ -x "$CONDA_EXE" ]; then return 0; fi
  for candidate in \
    "$HOME/miniconda3/bin/conda" \
    "/opt/miniconda3/bin/conda" \
    "$HOME/anaconda3/bin/conda" \
    "/opt/anaconda3/bin/conda"; do
    if [ -x "$candidate" ]; then CONDA_EXE="$candidate"; export CONDA_EXE; return 0; fi
  done
  CONDA_EXE="$(command -v conda 2>/dev/null || true)"
  if [ -n "$CONDA_EXE" ]; then export CONDA_EXE; return 0; fi
  echo "ERROR: Miniconda was not found. Install Miniconda first."
  return 1
}

find_vscode() {
  for candidate in \
    "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" \
    "$HOME/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"; do
    if [ -x "$candidate" ]; then CODE_EXE="$candidate"; export CODE_EXE; return 0; fi
  done
  CODE_EXE="$(command -v code 2>/dev/null || true)"
  if [ -n "$CODE_EXE" ]; then export CODE_EXE; return 0; fi
  echo "ERROR: Visual Studio Code was not found. Install it from https://code.visualstudio.com/"
  return 1
}

find_ollama() {
  for candidate in \
    "/Applications/Ollama.app/Contents/Resources/ollama" \
    "$HOME/Applications/Ollama.app/Contents/Resources/ollama" \
    "/usr/local/bin/ollama" \
    "/opt/homebrew/bin/ollama"; do
    if [ -x "$candidate" ]; then OLLAMA_EXE="$candidate"; export OLLAMA_EXE; return 0; fi
  done
  OLLAMA_EXE="$(command -v ollama 2>/dev/null || true)"
  if [ -n "$OLLAMA_EXE" ]; then export OLLAMA_EXE; return 0; fi
  return 1
}

ensure_ollama_running() {
  find_ollama || return 1
  if curl -fsS --max-time 2 http://127.0.0.1:11434/api/version >/dev/null 2>&1; then return 0; fi
  ollama_log_dir="$HOME/Library/Logs/ManagementScienceVSCode"
  mkdir -p "$ollama_log_dir"
  nohup "$OLLAMA_EXE" serve >"$ollama_log_dir/ollama.log" 2>&1 </dev/null &
  ollama_attempt=0
  while [ "$ollama_attempt" -lt 10 ]; do
    if curl -fsS --max-time 2 http://127.0.0.1:11434/api/version >/dev/null 2>&1; then return 0; fi
    sleep 1
    ollama_attempt=$((ollama_attempt + 1))
  done
  return 1
}
