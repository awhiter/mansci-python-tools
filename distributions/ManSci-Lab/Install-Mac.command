#!/bin/bash
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"; VERSION=2026.09.03.1
MARKER="$HOME/Library/Application Support/ManagementScience/Core/version.txt"
if [ ! -f "$MARKER" ] || [ "$(cat "$MARKER")" != "$VERSION" ]; then MANSCI_EMBEDDED=1 bash "$ROOT/payload/core/Install-Mac.command" || exit 1; fi
CONDA="$(cat "$HOME/Library/Application Support/ManagementScience/Core/conda-path.txt")"
"$CONDA" run --no-capture-output -n mansci-python python -m pip install --upgrade --upgrade-strategy only-if-needed -r "$ROOT/payload/requirements-student.txt" || exit 1
SUPPORT="$HOME/Library/Application Support/ManagementScience/Lab"; mkdir -p "$SUPPORT"
ditto "$ROOT/payload/personas" "$SUPPORT/personas"; ditto "$ROOT/payload/jupyter-config" "$SUPPORT/jupyter-config"
cp -f "$ROOT/payload/student_lab.py" "$SUPPORT/student_lab.py"; cp -f "$ROOT/payload/launch-mac.command" "$SUPPORT/launch.command"; chmod +x "$SUPPORT/launch.command"
APP="$HOME/Applications/ManSci Lab.app"; mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp -f "$ROOT/payload/icons/jupyterlab.icns" "$APP/Contents/Resources/jupyterlab.icns"; cp -f "$SUPPORT/launch.command" "$APP/Contents/MacOS/launch"; chmod +x "$APP/Contents/MacOS/launch"
/usr/libexec/PlistBuddy -c 'Clear dict' "$APP/Contents/Info.plist" 2>/dev/null || true
/usr/libexec/PlistBuddy -c 'Add :CFBundleName string ManSci Lab' -c 'Add :CFBundleIdentifier string uk.ac.ucl.mansci.lab' -c 'Add :CFBundleExecutable string launch' -c 'Add :CFBundleIconFile string jupyterlab.icns' -c 'Add :CFBundleVersion string 2026.09.03.2' -c 'Add :CFBundleShortVersionString string 2026.09.03.2' "$APP/Contents/Info.plist"
xattr -cr "$APP"; codesign --force --deep --sign - "$APP"; ditto "$APP" "$HOME/Desktop/ManSci Lab.app"; xattr -cr "$HOME/Desktop/ManSci Lab.app"; codesign --force --deep --sign - "$HOME/Desktop/ManSci Lab.app"
touch "$APP" "$HOME/Desktop/ManSci Lab.app"
LSREGISTER="/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
[ -x "$LSREGISTER" ] && "$LSREGISTER" -f "$APP" "$HOME/Desktop/ManSci Lab.app"
killall Finder >/dev/null 2>&1 || true
echo "ManSci Lab installed."
[ "${MANSCI_EMBEDDED:-0}" = 1 ] || read -r -p "Press Return to close..."
