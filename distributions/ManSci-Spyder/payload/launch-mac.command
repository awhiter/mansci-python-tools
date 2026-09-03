#!/bin/bash
CONDA="$(cat "$HOME/Library/Application Support/ManagementScience/Core/conda-path.txt")"
HOME_FILE="$HOME/Documents/ManSci Code Home.txt"; WORK="$HOME/Documents/ManSci Code"
[ -f "$HOME_FILE" ] && WORK="$(head -1 "$HOME_FILE")"
export SPYDER_CONFDIR="$HOME/Library/Application Support/ManagementScience/Spyder"
cd "$WORK" || exit 1
exec "$CONDA" run --no-capture-output -n mansci-python spyder --new-instance
