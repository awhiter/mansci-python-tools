"""Opt-in native renderer smoke test; hidden window and temporary storage."""
import os
import tempfile
import threading
import sys
import webview

if sys.platform == 'darwin':
    import AppKit
    if AppKit.NSScreen.mainScreen() is None:
        print('SKIP: no graphical desktop is available to this test process.')
        sys.exit(77)

finished = threading.Event()
errors = []
window = webview.create_window('ManSci renderer test', html='<h1 id="ready">ManSci</h1>', hidden=True)

def watchdog():
    if not finished.wait(45):
        print('Native renderer timed out', flush=True)
        os._exit(1)

def verify():
    try:
        if not window.events.loaded.wait(25): raise RuntimeError('Page did not load')
        assert window.evaluate_js('document.getElementById("ready").textContent') == 'ManSci'
        print('Native renderer HTML/JavaScript PASS', flush=True)
    except Exception as error:
        errors.append(str(error))
    finally:
        window.destroy()

threading.Thread(target=watchdog, daemon=True).start()
try:
    with tempfile.TemporaryDirectory(prefix='mansci-webview-') as storage:
        webview.start(verify, gui='edgechromium' if os.name == 'nt' else 'cocoa', storage_path=storage, private_mode=True)
finally:
    finished.set()
if errors: raise RuntimeError('; '.join(errors))
