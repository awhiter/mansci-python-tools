#!/bin/bash
set -u
CONDA="$(cat "$HOME/Library/Application Support/ManagementScience/Core/conda-path.txt" 2>/dev/null)"
SCRIPT="$HOME/Library/Application Support/ManagementScience/Staff-Lab/staff_lab.py"
if [ ! -x "$CONDA" ] || [ ! -f "$SCRIPT" ]; then echo 'Staff Lab is not installed. Run its installer first.'; read -r -p 'Press Return...'; exit 1; fi
"$CONDA" run --no-capture-output -n mansci-python python "$SCRIPT" forget-key
echo 'Rerun the Staff Lab installer to enter and test replacement Azure details.'
read -r -p 'Press Return to close...'
