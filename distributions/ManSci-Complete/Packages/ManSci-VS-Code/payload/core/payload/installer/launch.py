"""Start a managed tool, logging failures without a visible terminal."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import urlopen

def main():
    here = Path(__file__).resolve().parent
    cfg = json.loads((here / 'launch-config.json').read_text())
    support = (Path.home() / 'Library/Application Support/ManagementScience' if sys.platform == 'darwin'
               else Path(os.environ['LOCALAPPDATA']) / 'ManagementScience')
    logs = support / 'Logs'; logs.mkdir(parents=True, exist_ok=True)
    with (logs / 'launch.log').open('a', buffering=1) as log:
        # Child servers must inherit the log too, not a hidden/closed terminal.
        os.dup2(log.fileno(), 1)
        os.dup2(log.fileno(), 2)
        sys.stdout = sys.stderr = log
        try:
            pointer = Path.home() / 'Documents/ManSci Code Home.txt'
            home = Path(os.path.expandvars(pointer.read_text().strip())).expanduser() if pointer.exists() else Path.home() / 'Documents/ManSci Code'
            home.mkdir(parents=True, exist_ok=True)
            os.chdir(home)
            if cfg['kind'] == 'Spyder':
                os.environ['SPYDER_CONFDIR'] = str(support / 'Spyder')
                from spyder.config.manager import CONF
                for key, value in {'startup/use_project_or_home_directory': False,
                                   'startup/use_fixed_directory': True, 'startup/fixed_directory': str(home)}.items():
                    CONF.set('workingdir', key, value)
                CONF.set('main_interpreter', 'default', True)
                CONF.set('main_interpreter', 'custom', False)
                executable = Path(sys.prefix) / ('Scripts/spyder.exe' if os.name == 'nt' else 'bin/spyder')
                return subprocess.call([str(executable), '--new-instance'], stdout=log, stderr=log)
            if cfg['kind'] == 'Lab':
                os.environ['PATH'] = str(Path(cfg['ollama']).parent) + os.pathsep + os.environ.get('PATH', '')
                import student_lab
                return student_lab.launch()
            try:
                with urlopen('http://127.0.0.1:11434/api/tags', timeout=2): pass
            except OSError:
                options = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {'start_new_session': True}
                subprocess.Popen([cfg['ollama'], 'serve'], stdin=subprocess.DEVNULL, stdout=log, stderr=log, **options)
            import vscode_setup
            vscode_setup.launch(cfg['code'])
            return 0
        except Exception:
            import traceback
            traceback.print_exc()
            return 1

if __name__ == '__main__': raise SystemExit(main())
