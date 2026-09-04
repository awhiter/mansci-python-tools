"""Synchronise embedded components, write entry points and build release ZIPs."""
from pathlib import Path
import hashlib
import shutil
import zipfile
import json

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'distributions'
OUT = ROOT / 'release-assets'

def entrypoints(folder, kind):
    prefix = 'Install-All' if kind == 'Complete' else 'Install'
    (folder / 'README.md').write_text(f'''# ManSci {kind} — staff-testing installer

Extract the whole ZIP to a local folder and close ManSci tools before updating.
Run **{prefix}-Windows.bat** in Windows or **{prefix}-Mac.command** on Mac.

**Mac security message:** “Apple could not verify…” is expected because this
installer is not Apple-notarised; it does not itself mean malware was detected.
Only for a download from your teaching team's link: click **Done**, then open
**System Settings → Privacy & Security → Security → Open Anyway** for
**{prefix}-Mac.command**. Authenticate if asked and confirm **Open**.
Do not disable general security protections. If approval is unavailable, or a
warning says malware was detected or the software will damage your computer,
stop and contact the teaching team. Read the full explanation and troubleshooting
in **DISTRIBUTION-GUIDE.md** before proceeding.

**Windows:** those approval steps are Mac-only. Windows may display its own
installation or security prompts; a permission prompt is not a safety guarantee.
Contact the teaching team about unexpected security warnings.

The guided installer checks prerequisites first, offers installation where supported,
asks for consent to required terms, prepares Python and local AI, then creates launchers.
Keep its window open and watch for prompts. Several stages can take many minutes.
For Ollama choose **local use**, not sign-in; its service starts automatically.

Windows taskbar pins are optional: after installing a tool, find its **ManSci**
entry in Start, right-click and choose **Pin to taskbar** (possibly under **More**).
The installer never changes your pins. Pin the ManSci entry, not the ordinary
running ordinary VS Code icon. Lab now opens its own reusable window; ManSci Code
windows receive the same taskbar identity as their launcher. When upgrading from
an earlier release, manually replace old pins with the new Start entries, including
Spyder/Python pins: Spyder now also retains its ManSci identity and relaunch command.

Read **DISTRIBUTION-GUIDE.md** for the five stages, manual fallback instructions,
architecture information and automatic log locations. On failure the window stays open.
Rerun after resolving the error; student work and existing model data are preserved.

All tools share Documents/ManSci Code and mansci-python. Core supplies test.py,
test.ipynb and a folder README without overwriting existing work.
This is for staff testing, not yet approved for student rollout.
''')
    shutil.copy2(ROOT / 'DISTRIBUTION-GUIDE.md', folder / 'DISTRIBUTION-GUIDE.md')
    bat = folder / (prefix + '-Windows.bat')
    bat.write_bytes(('''@echo off
setlocal
echo Management Science guided installer
echo Keep this window open and watch for prompts. Installation can take many minutes.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0payload\\installer\\bootstrap-windows.ps1" -PackageRoot "%~dp0." -Kind "''' + kind + '''"
set "MANSCI_RESULT=%ERRORLEVEL%"
if not "%MANSCI_RESULT%"=="0" echo Installation did not complete. Read the message above and share the displayed log with staff.
echo This window will remain open until you press a key.
pause
exit /b %MANSCI_RESULT%
''').replace('\n','\r\n').encode('utf-8'))
    mac = folder / (prefix + '-Mac.command')
    mac.write_text('''#!/bin/bash
ROOT="$(cd "$(dirname "$0")" && pwd)"
bash "$ROOT/payload/installer/bootstrap-mac.sh" "$ROOT" "''' + kind + '''"
RESULT=$?
if [ "$RESULT" -ne 0 ]; then
  echo "Installation did not complete. Read the error above."
  echo "Logs: $HOME/Library/Logs/ManagementScience"
fi
read -r -p "Press Return to close this window..."
exit "$RESULT"
''')
    mac.chmod(0o755)
    shutil.copytree(ROOT / 'installer', folder / 'payload/installer', dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))

def main():
    helper = ROOT / 'installer/vscode-startup'
    metadata = json.loads((helper / 'package.json').read_text())
    vsix = DIST / 'ManSci-VS-Code/payload/mansci-startup.vsix'
    with zipfile.ZipFile(vsix, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="json" ContentType="application/json"/><Default Extension="js" ContentType="application/javascript"/><Default Extension="vsixmanifest" ContentType="text/xml"/></Types>')
        z.writestr('extension.vsixmanifest', f'''<?xml version="1.0"?><PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011"><Metadata><Identity Language="en-US" Id="startup" Version="{metadata['version']}" Publisher="mansci"/><DisplayName>ManSci Startup</DisplayName><Description xml:space="preserve">Managed Python and notebook selection</Description><Properties><Property Id="Microsoft.VisualStudio.Code.Engine" Value="^1.95.0"/></Properties></Metadata><Installation><InstallationTarget Id="Microsoft.VisualStudio.Code"/></Installation><Dependencies/><Assets><Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true"/></Assets></PackageManifest>''')
        for name in ('package.json', 'extension.js'):
            z.write(helper / name, 'extension/' + name)
    entrypoints(DIST / 'ManSci-Core', 'Core')
    for kind in ('Spyder','Lab','VS-Code'):
        folder = DIST / ('ManSci-' + kind)
        entrypoints(folder, kind)
        shutil.copytree(DIST / 'ManSci-Core', folder / 'payload/core', dirs_exist_ok=True)
    complete = DIST / 'ManSci-Complete'
    entrypoints(complete, 'Complete')
    for kind in ('Core','Spyder','Lab','VS-Code'):
        shutil.copytree(DIST / ('ManSci-' + kind), complete / 'Packages' / ('ManSci-' + kind), dirs_exist_ok=True)
    shutil.copy2(ROOT / 'DISTRIBUTION-GUIDE.md', complete / 'OVERALL-GUIDE.md')
    OUT.mkdir(exist_ok=True)
    sums = []
    for kind in ('Complete','Core','Lab','Spyder','VS-Code'):
        folder = DIST / ('ManSci-' + kind)
        archive = OUT / (folder.name + '.zip')
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
            for f in sorted(folder.rglob('*')):
                if f.is_file() and f.name != '.DS_Store' and '__pycache__' not in f.parts and f.suffix != '.pyc':
                    z.write(f, f.relative_to(DIST))
        with zipfile.ZipFile(archive) as z: assert z.testzip() is None
        sums.append(hashlib.sha256(archive.read_bytes()).hexdigest() + '  ' + archive.name)
    (ROOT / 'SHA256SUMS.txt').write_text('\n'.join(sums) + '\n')
    shutil.copy2(ROOT / 'SHA256SUMS.txt', OUT / 'SHA256SUMS.txt')
    print('Built five archives in', OUT)

if __name__ == '__main__': main()
