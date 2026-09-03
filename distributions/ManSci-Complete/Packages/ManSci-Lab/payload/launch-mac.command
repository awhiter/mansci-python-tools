#!/bin/bash
CONDA="$(cat "$HOME/Library/Application Support/ManagementScience/Core/conda-path.txt")"
ROOT="$HOME/Library/Application Support/ManagementScience/Lab"
exec "$CONDA" run --no-capture-output -n mansci-python python "$ROOT/student_lab.py" launch
