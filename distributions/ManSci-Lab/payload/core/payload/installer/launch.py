"""Start a managed tool, logging failures without a visible terminal."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import urlopen

def runtime_executable(kind, configured, current):
    # Jupyter Client detects pythonw here to apply CREATE_NO_WINDOW to Spyder's
    # kernel processes. Spyder itself converts pythonw to python for kernel argv.
    return current if kind == 'Spyder' else configured

def main():
    here = Path(__file__).resolve().parent
    cfg = json.loads((here / 'launch-config.json').read_text(encoding='utf-8'))
    os.environ.update(cfg.get('activation', {}))
    sys.executable = runtime_executable(cfg['kind'], cfg.get('python', sys.executable), sys.executable)
    support = (Path.home() / 'Library/Application Support/ManagementScience' if sys.platform == 'darwin'
               else Path(os.environ['LOCALAPPDATA']) / 'ManagementScience')
    logs = support / 'Logs'; logs.mkdir(parents=True, exist_ok=True)
    with (logs / 'launch.log').open('a', buffering=1, encoding='utf-8') as log:
        # Child servers must inherit the log too, not a hidden/closed terminal.
        os.dup2(log.fileno(), 1)
        os.dup2(log.fileno(), 2)
        sys.stdout = sys.stderr = log
        try:
            pointer = Path.home() / 'Documents/ManSci Code Home.txt'
            home = Path(os.path.expandvars(pointer.read_text(encoding='utf-8').strip())).expanduser() if pointer.exists() else Path.home() / 'Documents/ManSci Code'
            home.mkdir(parents=True, exist_ok=True)
            os.chdir(home)
            if cfg['kind'] == 'Spyder':
                sys.argv = ['spyder', '--new-instance']
                os.environ['SPYDER_CONFDIR'] = str(support / 'Spyder')
                from spyder.config.manager import CONF
                for key, value in {'startup/use_project_or_home_directory': False,
                                   'startup/use_fixed_directory': True, 'startup/fixed_directory': str(home)}.items():
                    CONF.set('workingdir', key, value)
                CONF.set('main_interpreter', 'default', True)
                CONF.set('main_interpreter', 'custom', False)
                # Run in the existing windowless process; do not spawn a console
                # executable. Show Files after Spyder restores its saved layout.
                from spyder.app import mainwindow
                original = mainwindow.MainWindow.post_visible_setup
                def show_files(window):
                    original(window)
                    try:
                        plugin = window.get_plugin('explorer')
                        plugin.chdir(str(home))
                        plugin.dockwidget.show()
                        plugin.dockwidget.raise_()
                        plugin.change_visibility(True, force_focus=False)
                    except Exception:
                        import traceback
                        traceback.print_exc()
                mainwindow.MainWindow.post_visible_setup = show_files
                from spyder.app.start import main as spyder_main
                return spyder_main() or 0
            if cfg['kind'] == 'Lab':
                os.environ['PATH'] = str(Path(cfg['ollama']).parent) + os.pathsep + os.environ.get('PATH', '')
                import student_lab
                return student_lab.launch()
            try:
                with urlopen('http://127.0.0.1:11434/api/tags', timeout=2): pass
            except OSError:
                options = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {'start_new_session': True}
                subprocess.Popen([cfg['ollama'], 'serve'], stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                 env=dict(os.environ, OLLAMA_HOST='127.0.0.1:11434'), **options)
            import vscode_setup
            vscode_setup.launch(cfg['code'])
            return 0
        except Exception:
            import traceback
            traceback.print_exc()
            return 1

if __name__ == '__main__': raise SystemExit(main())
