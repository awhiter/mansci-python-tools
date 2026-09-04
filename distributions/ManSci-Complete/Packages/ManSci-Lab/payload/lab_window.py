"""One native Lab window per user, with authenticated localhost focus IPC."""
import hmac
import html
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import threading
import time


class WindowOwner:
    def __init__(self, root):
        self.root = root
        root.mkdir(parents=True, exist_ok=True)
        self.file = (root / 'desktop-window.lock').open('a+b')
        self.info = root / 'desktop-window.json'
        self.socket = None
        self.owned = False
        self.focus = threading.Event()
        self.stop = threading.Event()

    def acquire(self):
        try:
            if os.name == 'nt':
                import msvcrt
                self.file.seek(0, 2)
                if self.file.tell() == 0:
                    self.file.write(b'0'); self.file.flush()
                self.file.seek(0)
                msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.owned = True
            return True
        except OSError:
            return False

    def request_focus(self, timeout=15):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                data = json.loads(self.info.read_text(encoding='utf-8'))
                with socket.create_connection(('127.0.0.1', int(data['port'])), timeout=1) as client:
                    client.sendall(('focus ' + data['token'] + '\n').encode('ascii'))
                    if client.recv(16) == b'OK':
                        return True
            except (OSError, ValueError, KeyError):
                pass
            time.sleep(0.2)
        return False

    def listen(self):
        token = secrets.token_urlsafe(32)
        self.socket = socket.socket()
        self.socket.bind(('127.0.0.1', 0))
        self.socket.listen(4)
        self.socket.settimeout(0.5)
        temporary = self.info.with_suffix('.tmp')
        temporary.write_text(json.dumps({'port': self.socket.getsockname()[1], 'token': token}), encoding='utf-8')
        if os.name != 'nt': temporary.chmod(0o600)
        temporary.replace(self.info)
        def serve():
            while not self.stop.is_set():
                try:
                    client, _ = self.socket.accept()
                    with client:
                        client.settimeout(1)
                        request = client.recv(512).decode('ascii').strip()
                        if hmac.compare_digest(request, 'focus ' + token):
                            self.focus.set()
                            client.sendall(b'OK')
                except (OSError, UnicodeError):
                    continue
        threading.Thread(target=serve, daemon=True).start()

    def close(self):
        self.stop.set()
        if self.socket: self.socket.close()
        if self.owned:
            self.info.unlink(missing_ok=True)
        self.file.close()  # releases OS lock, including after a crash


def wait_for_server(lab, runtime, workspace, stop):
    if stop.is_set(): raise RuntimeError('Lab window closed during startup.')
    existing = lab.running_server_url(runtime, workspace)
    if existing: return existing
    env = dict(os.environ, JUPYTER_CONFIG_DIR=str(Path(lab.__file__).parent / 'jupyter-config'),
               JUPYTER_DATA_DIR=str(lab.data_dir() / 'jupyter-data'),
               JUPYTER_RUNTIME_DIR=str(runtime), PYTHONNOUSERSITE='1')
    logs = lab.data_dir() / 'logs'; logs.mkdir(parents=True, exist_ok=True)
    options = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {'start_new_session': True}
    with (logs / 'lab-server.log').open('a', encoding='utf-8') as log:
        child = subprocess.Popen([sys.executable, '-m', 'jupyterlab',
            f'--ServerApp.root_dir={workspace}', '--ServerApp.open_browser=False'],
            env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=log, **options)
    ready = False
    try:
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            if stop.is_set(): raise RuntimeError('Lab window closed during startup.')
            url = lab.running_server_url(runtime, workspace)
            if url:
                ready = True
                return url
            if child.poll() is not None:
                raise RuntimeError(f'JupyterLab stopped during startup. See {logs / "lab-server.log"}')
            stop.wait(0.5)
        raise RuntimeError(f'JupyterLab did not become ready. See {logs / "lab-server.log"}')
    finally:
        # Only stop a server we just created that never reached readiness.
        # Never stop a reused server or a running notebook session on window close.
        if not ready and child.poll() is None:
            child.terminate()
            try: child.wait(timeout=5)
            except subprocess.TimeoutExpired: pass


def run():
    import student_lab as lab
    owner = WindowOwner(lab.data_dir())
    workers = []
    try:
        if not owner.acquire():
            if owner.request_focus(): return 0
            raise RuntimeError('The existing ManSci Lab window is not responding. Close it normally before retrying.')
        owner.listen()
        import webview
        webview.settings['ALLOW_DOWNLOADS'] = True
        window = webview.create_window('ManSci Lab', width=1200, height=800,
            min_size=(700, 500), confirm_close=True, text_select=True, zoomable=True,
            html='<h2>Starting ManSci Lab…</h2><p>Please wait while the local notebook server starts.</p>')
        window.events.closed += owner.stop.set
        def prepare():
            try:
                workspace = lab.documents_dir(); workspace.mkdir(parents=True, exist_ok=True)
                lab.install_local_persona(workspace); lab.write_private_kernelspec()
                runtime = lab.data_dir() / 'jupyter-runtime'; runtime.mkdir(parents=True, exist_ok=True)
                threading.Thread(target=lab.start_ollama, daemon=True).start()
                url = wait_for_server(lab, runtime, workspace, owner.stop)
                if not owner.stop.is_set(): window.load_url(url)
            except Exception as error:
                if not owner.stop.is_set():
                    window.load_html('<h2>ManSci Lab could not start</h2><p>' + html.escape(str(error)) + '</p><p>Close this window, resolve the error and relaunch.</p>')
        def service():
            worker = threading.Thread(target=prepare, daemon=True); workers.append(worker); worker.start()
            while not owner.stop.wait(0.2):
                if owner.focus.is_set():
                    owner.focus.clear()
                    window.restore(); window.show()
            worker.join(timeout=8)
        here = Path(__file__).resolve().parent
        icon = here / 'jupyterlab.ico'
        if sys.platform == 'darwin': icon = here / 'jupyterlab.icns'
        webview.start(service, gui='edgechromium' if os.name == 'nt' else 'cocoa',
            private_mode=False, storage_path=str(lab.data_dir() / 'desktop-webview'),
            icon=str(icon) if icon.is_file() else None)
        return 0
    finally:
        owner.stop.set()
        for worker in workers: worker.join(timeout=8)
        owner.close()
