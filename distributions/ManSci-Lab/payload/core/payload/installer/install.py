"""Shared, staged installer. Bootstrap first discovers/installs prerequisites."""
from __future__ import annotations
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.request import urlopen

VERSION = '2026.09.04.2'
CORE_VERSION = '2026.09.04.1'  # Teaching packages are unchanged in this launcher update.
MODEL = 'qwen2.5-coder:3b'
PACKAGES = ('numpy', 'pandas', 'scipy', 'statsmodels', 'matplotlib', 'sklearn',
            'sympy', 'openpyxl', 'networkx', 'seaborn', 'requests', 'spyder', 'jupyterlab', 'ipykernel', 'jupytext')

def support():
    return (Path.home() / 'Library/Application Support/ManagementScience' if sys.platform == 'darwin'
            else Path(os.environ['LOCALAPPDATA']) / 'ManagementScience')

def run(args, *, capture=False, env=None):
    try:
        result = subprocess.run([str(a) for a in args], check=True, text=True,
                                capture_output=capture, env=env)
    except subprocess.CalledProcessError as exc:
        if capture:
            print(exc.stdout or '')
            print(exc.stderr or '')
        raise
    return result.stdout.strip() if capture else ''

def consent(message):
    if input(message + ' [y/N] ').strip().lower() not in ('y', 'yes'):
        raise RuntimeError('Consent declined. Installation stopped without accepting these terms.')

def data_from_ollama():
    try:
        with urlopen('http://127.0.0.1:11434/api/tags', timeout=2) as response:
            return json.load(response)
    except (OSError, ValueError):
        return None

def prepare_model(executable):
    print('[4/5] Starting the local AI service automatically. No terminal command or sign-in is needed.')
    if data_from_ollama() is None:
        logs = support() / 'Logs'
        logs.mkdir(parents=True, exist_ok=True)
        with (logs / 'ollama-service.log').open('a') as log:
            options = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {'start_new_session': True}
            local_env = dict(os.environ, OLLAMA_HOST='127.0.0.1:11434')
            subprocess.Popen([executable, 'serve'], stdin=subprocess.DEVNULL, stdout=log, stderr=log, env=local_env, **options)
        for _ in range(60):
            if data_from_ollama() is not None:
                break
            time.sleep(1)
        else:
            raise RuntimeError(f'Ollama did not respond within 60 seconds. See {logs / "ollama-service.log"}. Rerun after resolving this; do not sign in.')
    models = data_from_ollama() or {}
    if any(m.get('name') == MODEL for m in models.get('models', [])):
        print(f'PASS: {MODEL} already installed; reusing it, not downloading again.')
        return
    print('Downloading Qwen2.5-Coder 3B, approximately 2 GB. This can take many minutes.')
    print('The model is a local Python coding assistant, not a paid cloud service.')
    print('Messages such as pulling <letters/numbers> and progress bars are NORMAL. Keep this window open.')
    run([executable, 'pull', MODEL])
    if not any(m.get('name') == MODEL for m in (data_from_ollama() or {}).get('models', [])):
        raise RuntimeError('Ollama finished without reporting the required model. Rerun to retry.')
    print('PASS: local AI model ready.')

def core_payload(package, kind):
    if kind == 'Complete': return package / 'Packages/ManSci-Core/payload'
    if kind == 'Core': return package / 'payload'
    return package / 'payload/core/payload'

def install_core(conda, payload, ollama):
    root = support() / 'Core'
    root.mkdir(parents=True, exist_ok=True)
    (root / 'conda-path.txt').write_text(conda + '\n', encoding='utf-8')
    marker = root / 'version.txt'
    healthy = False
    if marker.exists() and marker.read_text().strip() == CORE_VERSION:
        try:
            run([conda, 'run', '-n', 'mansci-python', 'python', '-c',
                 'import sys; assert sys.version_info[:2] == (3,13); ' + '; '.join('import ' + m for m in PACKAGES)], capture=True)
            healthy = True
        except subprocess.CalledProcessError:
            print('Core marker exists, but a runtime check failed. Repairing Core.')
    if not healthy:
        print('[2/5] Anaconda channel terms. You must decide whether to accept; we do not accept silently.')
        print('Review: https://www.anaconda.com/legal and https://www.anaconda.com/docs/getting-started/tos-plugin')
        channels = ['https://repo.anaconda.com/pkgs/main', 'https://repo.anaconda.com/pkgs/r']
        if os.name == 'nt': channels.append('https://repo.anaconda.com/pkgs/msys2')
        plugin = subprocess.run([conda, 'tos', '--help'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
        if plugin:
            for channel in channels:
                run([conda, 'tos', 'view', '--override-channels', '--channel', channel])
            consent('Do you accept the displayed Anaconda channel terms so this installer can record your consent?')
            for channel in channels:
                run([conda, 'tos', 'accept', '--override-channels', '--channel', channel])
        else:
            print('This Conda version has no ToS plugin. Review and answer any terms prompts from Conda itself.')
        print('[3/5] Preparing Python and teaching packages. Solving/downloading may take many minutes.')
        environments = json.loads(run([conda, 'env', 'list', '--json'], capture=True))['envs']
        exists = any(Path(p).name == 'mansci-python' for p in environments)
        command = [conda, 'env', 'update' if exists else 'create', '--name', 'mansci-python', '--file', payload / 'environment.yml']
        run(command)
    else:
        print('[2/5] Core is current; no new channel operation or acceptance is needed.')
        print('[3/5] PASS: reusing the verified mansci-python environment.')
    run([conda, 'run', '--no-capture-output', '-n', 'mansci-python', 'python', payload / 'core_setup.py', 'initialise'])
    run([conda, 'run', '--no-capture-output', '-n', 'mansci-python', 'python', '-c',
         'import sys; assert sys.version_info[:2] == (3,13); ' + '; '.join('import ' + m for m in PACKAGES)])
    prepare_model(ollama)
    marker.write_text(CORE_VERSION + '\n', encoding='utf-8')
    return run([conda, 'run', '-n', 'mansci-python', 'python', '-c', 'import sys; print(sys.executable)'], capture=True)

def install_tool(kind, source, conda, python, code, ollama):
    print(f'[5/5] Configuring {kind} and creating its launcher...')
    if kind == 'VS-Code':
        root = (Path.home() / 'Library/Application Support/ManagementScienceVSCode' if sys.platform == 'darwin'
                else Path(os.environ['LOCALAPPDATA']) / 'ManagementScienceVSCode')
        target = root / 'launcher'
        names = ('vscode_setup.py', 'STUDENT-GUIDE.md', 'student-profile-check.py', 'mansci-startup.vsix')
        title, icon = 'ManSci VS Code', 'vscode'
    else:
        root = support() / kind
        target = root
        names = ('student_lab.py',) if kind == 'Lab' else ('spyder_setup.py',)
        title, icon = ('ManSci Lab', 'jupyterlab') if kind == 'Lab' else ('ManSci Spyder', 'spyder')
    target.mkdir(parents=True, exist_ok=True)
    for name in names: shutil.copy2(source / name, target / name)
    if kind == 'Lab':
        run([conda, 'run', '--no-capture-output', '-n', 'mansci-python', 'python', '-m', 'pip', 'install',
             '--upgrade-strategy', 'only-if-needed', '-r', source / 'requirements-student.txt'])
        for directory in ('personas', 'jupyter-config'):
            shutil.copytree(source / directory, target / directory, dirs_exist_ok=True)
    if kind == 'VS-Code':
        for action in ('configure', 'install-extensions'):
            run([conda, 'run', '--no-capture-output', '-n', 'mansci-python', 'python', target / 'vscode_setup.py', action,
                 '--conda', conda, '--code', code, '--source', target])
    if kind == 'Spyder':
        run([conda, 'run', '--no-capture-output', '-n', 'mansci-python', 'python', target / 'spyder_setup.py'])
    shutil.copy2(Path(__file__).with_name('launch.py'), target / 'launch.py')
    # Capture only activation-related values, never the user's full environment
    # (which may include credentials). Do this once at installation, not launch.
    activation = json.loads(run([conda, 'run', '-n', 'mansci-python', 'python', '-c',
        'import os,json; keys=("PATH","CONDA_PREFIX","CONDA_DEFAULT_ENV","CONDA_SHLVL"); '
        'print(json.dumps({k:os.environ[k] for k in keys if k in os.environ}))'], capture=True))
    (target / 'launch-config.json').write_text(json.dumps({'kind': kind, 'code': code, 'ollama': ollama,
        'python': python, 'activation': activation}), encoding='utf-8')
    if os.name == 'nt':
        shutil.copy2(Path(__file__).with_name('hidden.vbs'), target / 'hidden.vbs')
        launch = target / 'launch.py'
        pythonw = Path(python).with_name('pythonw.exe')
        if not pythonw.is_file(): raise RuntimeError(f'Windowless Python is missing: {pythonw}')
        shutil.copy2(source / 'icons' / (icon + '.ico'), target / (icon + '.ico'))
        run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', Path(__file__).with_name('shortcut.ps1'),
             '-Name', title, '-Launcher', launch, '-Python', pythonw, '-Icon', target / (icon + '.ico'), '-Wrapper', target / 'hidden.vbs'])
    else:
        import plistlib
        import shlex
        for parent in (Path.home() / 'Applications', Path.home() / 'Desktop'):
            app = parent / (title + '.app')
            if app.is_symlink():
                backup = app.with_name(app.name + '.previous-' + str(time.time_ns()))
                app.rename(backup)
                print(f'Preserved old launcher alias at {backup}')
            (app / 'Contents/MacOS').mkdir(parents=True, exist_ok=True)
            (app / 'Contents/Resources').mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / 'icons' / (icon + '.icns'), app / 'Contents/Resources' / (icon + '.icns'))
            entry = app / 'Contents/MacOS/launch'
            entry.write_text('#!/bin/bash\nulimit -n 4096 2>/dev/null || true\nexec ' + shlex.quote(python) + ' ' + shlex.quote(str(target / 'launch.py')) + '\n')
            entry.chmod(0o755)
            with (app / 'Contents/Info.plist').open('wb') as f:
                plistlib.dump({'CFBundleName': title, 'CFBundleIdentifier': 'uk.ac.ucl.mansci.' + kind.lower(),
                              'CFBundleExecutable': 'launch', 'CFBundlePackageType': 'APPL',
                              'CFBundleIconFile': icon + '.icns', 'CFBundleVersion': VERSION}, f)
            run(['codesign', '--force', '--deep', '--sign', '-', app])
            app.touch()
            register = '/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister'
            if Path(register).exists(): run([register, '-f', app])
    print(f'PASS: {title} launcher created. Its files are in a permanent support folder.')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--package', required=True, type=Path)
    p.add_argument('--kind', required=True, choices=('Core', 'Spyder', 'Lab', 'VS-Code', 'Complete'))
    p.add_argument('--conda', required=True)
    args = p.parse_args()
    stage = 'preflight'
    try:
        ollama = os.environ.get('MANSCI_OLLAMA', '')
        code = os.environ.get('MANSCI_CODE', '')
        if not Path(ollama).is_file(): raise RuntimeError('Ollama prerequisite was not located. Rerun and follow the first-stage instructions.')
        if args.kind in ('VS-Code', 'Complete') and not Path(code).is_file(): raise RuntimeError('VS Code prerequisite is missing. Install it before continuing.')
        # Do not silently accept terms through inherited CI/auto-accept settings.
        for key in ('CONDA_PLUGINS_AUTO_ACCEPT_TOS', 'CONDA_TOS_ACCEPT', 'CI'):
            os.environ.pop(key, None)
        stage = 'shared Core and local AI'
        python = install_core(args.conda, core_payload(args.package, args.kind), ollama)
        kinds = ('Spyder', 'Lab', 'VS-Code') if args.kind == 'Complete' else (() if args.kind == 'Core' else (args.kind,))
        for kind in kinds:
            stage = kind
            source = args.package / ('Packages/ManSci-' + kind) / 'payload' if args.kind == 'Complete' else args.package / 'payload'
            install_tool(kind, source, args.conda, python, code, ollama)
        print('\nINSTALLATION COMPLETE: Python PASS | local AI PASS | requested launchers PASS')
        print('Use the ManSci desktop launchers. Keep code/data in Documents/ManSci Code.')
        print('Test test.py and test.ipynb there. A small local AI model may still make mistakes.')
        print('On macOS, Finder may need reopening to refresh cached icons.')
        return 0
    except (Exception, KeyboardInterrupt) as e:
        print(f'\nINSTALLATION NOT COMPLETE - stage: {stage}\n{e}')
        print('No student files were deleted. Resolve the error and rerun to resume.')
        print('Log: ' + os.environ.get('MANSCI_INSTALL_LOG', 'see the bootstrap window'))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
