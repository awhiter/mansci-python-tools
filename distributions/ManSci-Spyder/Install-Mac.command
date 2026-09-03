#!/bin/bash
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"; VERSION=2026.09.03.1
MARKER="$HOME/Library/Application Support/ManagementScience/Core/version.txt"
if [ ! -f "$MARKER" ] || [ "$(cat "$MARKER")" != "$VERSION" ]; then
  echo "Installing/updating the required ManSci Core..."
  MANSCI_EMBEDDED=1 bash "$ROOT/payload/core/Install-Mac.command" || exit 1
fi
CONDA="$(cat "$HOME/Library/Application Support/ManagementScience/Core/conda-path.txt")"
SUPPORT="$HOME/Library/Application Support/ManagementScience/Spyder"; mkdir -p "$SUPPORT"
cp -f "$ROOT/payload/launch-mac.command" "$SUPPORT/launch.command"; chmod +x "$SUPPORT/launch.command"
"$CONDA" run --no-capture-output -n mansci-python python "$ROOT/payload/spyder_setup.py" || exit 1
APP="$HOME/Applications/ManSci Spyder.app"; mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp -f "$ROOT/payload/icons/spyder.icns" "$APP/Contents/Resources/spyder.icns"
cp -f "$SUPPORT/launch.command" "$APP/Contents/MacOS/launch"; chmod +x "$APP/Contents/MacOS/launch"
/usr/libexec/PlistBuddy -c 'Clear dict' "$APP/Contents/Info.plist" 2>/dev/null || true
/usr/libexec/PlistBuddy -c 'Add :CFBundleName string ManSci Spyder' -c 'Add :CFBundleIdentifier string uk.ac.ucl.mansci.spyder' -c 'Add :CFBundleExecutable string launch' -c 'Add :CFBundleIconFile string spyder.icns' -c 'Add :CFBundleVersion string 2026.09.03.2' -c 'Add :CFBundleShortVersionString string 2026.09.03.2' "$APP/Contents/Info.plist"
xattr -cr "$APP"; codesign --force --deep --sign - "$APP"
ditto "$APP" "$HOME/Desktop/ManSci Spyder.app"; xattr -cr "$HOME/Desktop/ManSci Spyder.app"; codesign --force --deep --sign - "$HOME/Desktop/ManSci Spyder.app"
touch "$APP" "$HOME/Desktop/ManSci Spyder.app"
LSREGISTER="/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
[ -x "$LSREGISTER" ] && "$LSREGISTER" -f "$APP" "$HOME/Desktop/ManSci Spyder.app"
killall Finder >/dev/null 2>&1 || true
echo "ManSci Spyder installed."
[ "${MANSCI_EMBEDDED:-0}" = 1 ] || read -r -p "Press Return to close..."
