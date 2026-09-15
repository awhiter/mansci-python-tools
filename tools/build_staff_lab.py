"""Build the separate Azure-enabled staff distribution from shared components."""
from pathlib import Path
import hashlib
import shutil
import zipfile

from build_release import ROOT, DIST, entrypoints

SOURCE = DIST / 'ManSci-Staff-Lab'
OUTPUTS = ROOT / 'release-assets'
FOLDER = SOURCE
ARCHIVE = OUTPUTS / 'ManSci-Staff-Lab.zip'

def main():
    # Refresh the source package from the same Core and installer used by the
    # student distributions; deleted files cannot linger between builds.
    entrypoints(SOURCE, 'Staff-Lab')
    (SOURCE / 'README.md').write_text((ROOT / 'STAFF-LAB-README.md').read_text(encoding='utf-8'), encoding='utf-8')
    (SOURCE / 'DISTRIBUTION-GUIDE.md').unlink(missing_ok=True)
    shutil.copy2(ROOT / 'STAFF-LAB-GUIDE.md', SOURCE / 'STAFF-LAB-GUIDE.md')
    shutil.rmtree(SOURCE / 'payload/core', ignore_errors=True)
    shutil.copytree(DIST / 'ManSci-Core', SOURCE / 'payload/core')
    support = SOURCE / 'Support Tools'
    shutil.rmtree(support, ignore_errors=True)
    support.mkdir()
    for name in ('reset-azure-key-mac.command', 'reset-azure-key-windows.bat',
                 'repair-chat-mac.command', 'repair-chat-windows.bat'):
        shutil.copy2(SOURCE / 'payload' / name, support / name)
    for script in support.glob('*.command'): script.chmod(0o755)
    OUTPUTS.mkdir(exist_ok=True)
    if ARCHIVE.exists(): ARCHIVE.unlink()
    with zipfile.ZipFile(ARCHIVE, 'w', zipfile.ZIP_DEFLATED) as z:
        for file in sorted(FOLDER.rglob('*')):
            if file.is_file() and file.name != '.DS_Store' and '__pycache__' not in file.parts and file.suffix != '.pyc':
                z.write(file, file.relative_to(DIST))
    with zipfile.ZipFile(ARCHIVE) as z: assert z.testzip() is None
    digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    (OUTPUTS / 'ManSci-Staff-Lab-SHA256.txt').write_text(f'{digest}  {ARCHIVE.name}\n', encoding='utf-8')
    print(FOLDER)
    print(ARCHIVE)
    print(digest)

if __name__ == '__main__': main()
