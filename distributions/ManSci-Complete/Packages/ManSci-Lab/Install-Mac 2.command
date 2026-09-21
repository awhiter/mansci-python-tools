#!/bin/bash
ROOT="$(cd "$(dirname "$0")" && pwd)"
bash "$ROOT/payload/installer/bootstrap-mac.sh" "$ROOT" "Lab"
RESULT=$?
if [ "$RESULT" -ne 0 ]; then
  echo "Installation did not complete. Read the error above."
  echo "Logs: $HOME/Library/Logs/ManagementScience"
fi
read -r -p "Press Return to close this window..."
exit "$RESULT"
