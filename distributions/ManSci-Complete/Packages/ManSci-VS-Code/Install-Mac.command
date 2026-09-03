#!/bin/bash
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"; VERSION=2026.09.03.1
MARKER="$HOME/Library/Application Support/ManagementScience/Core/version.txt"
if [ ! -f "$MARKER" ] || [ "$(cat "$MARKER")" != "$VERSION" ]; then MANSCI_EMBEDDED=1 bash "$ROOT/payload/core/Install-Mac.command" || exit 1; fi
. "$ROOT/payload/macos-common.sh"
find_conda || exit 1
if ! find_vscode; then
  echo "Install Visual Studio Code from https://code.visualstudio.com/ then rerun this installer."
  open https://code.visualstudio.com/ || true
  read -r -p "Press Return to close..."; exit 1
fi
SUPPORT="$HOME/Library/Application Support/ManagementScienceVSCode"; LAUNCHER="$SUPPORT/launcher"; mkdir -p "$LAUNCHER"
cp -f "$ROOT/payload/"{vscode_setup.py,launch-vscode-mac.command,check-vscode-mac.command,macos-common.sh,STUDENT-GUIDE.md,student-profile-check.py} "$LAUNCHER/"
chmod +x "$LAUNCHER/"*.command "$LAUNCHER/macos-common.sh"
MANSCI_VSCODE_SUPPORT="$SUPPORT" "$CONDA_EXE" run --no-capture-output -n mansci-python python "$LAUNCHER/vscode_setup.py" configure --conda "$CONDA_EXE" --code "$CODE_EXE" --source "$LAUNCHER" || exit 1
MANSCI_VSCODE_SUPPORT="$SUPPORT" "$CONDA_EXE" run --no-capture-output -n mansci-python python "$LAUNCHER/vscode_setup.py" install-extensions --conda "$CONDA_EXE" --code "$CODE_EXE" --source "$LAUNCHER" || exit 1
APP="$HOME/Applications/ManSci VS Code.app"; mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp -f "$ROOT/payload/icons/vscode.icns" "$APP/Contents/Resources/vscode.icns"; cp -f "$ROOT/payload/app-launch-mac" "$APP/Contents/MacOS/launch"; chmod +x "$APP/Contents/MacOS/launch"
/usr/libexec/PlistBuddy -c 'Clear dict' "$APP/Contents/Info.plist" 2>/dev/null || true
/usr/libexec/PlistBuddy -c 'Add :CFBundleName string ManSci VS Code' -c 'Add :CFBundleIdentifier string uk.ac.ucl.mansci.vscode' -c 'Add :CFBundleExecutable string launch' -c 'Add :CFBundleIconFile string vscode.icns' -c 'Add :CFBundleVersion string 2026.09.03.2' -c 'Add :CFBundleShortVersionString string 2026.09.03.2' "$APP/Contents/Info.plist"
xattr -cr "$APP"; codesign --force --deep --sign - "$APP"; ditto "$APP" "$HOME/Desktop/ManSci VS Code.app"; xattr -cr "$HOME/Desktop/ManSci VS Code.app"; codesign --force --deep --sign - "$HOME/Desktop/ManSci VS Code.app"
touch "$APP" "$HOME/Desktop/ManSci VS Code.app"
LSREGISTER="/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
[ -x "$LSREGISTER" ] && "$LSREGISTER" -f "$APP" "$HOME/Desktop/ManSci VS Code.app"
killall Finder >/dev/null 2>&1 || true
echo "ManSci VS Code installed with the Light+ theme."
[ "${MANSCI_EMBEDDED:-0}" = 1 ] || read -r -p "Press Return to close..."
