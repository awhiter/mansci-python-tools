import importlib.util
from pathlib import Path
import tempfile
import threading
import socket
import json
import unittest
from unittest.mock import patch, Mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('lab_window', ROOT / 'distributions/ManSci-Lab/payload/lab_window.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class WindowTests(unittest.TestCase):
    def test_second_launcher_focuses_owner_and_lock_releases(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = m.WindowOwner(root); second = m.WindowOwner(root)
            try:
                self.assertTrue(first.acquire()); first.listen()
                self.assertFalse(second.acquire())
                self.assertTrue(second.request_focus(timeout=2))
                self.assertTrue(first.focus.wait(1))
                second.close(); first.close()
                third = m.WindowOwner(root)
                self.assertTrue(third.acquire()); third.close()
            finally:
                if not first.file.closed: first.close()
                if not second.file.closed: second.close()

    def test_unauthenticated_focus_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            first = m.WindowOwner(Path(directory))
            try:
                first.acquire(); first.listen()
                port = json.loads(first.info.read_text())['port']
                with socket.create_connection(('127.0.0.1', port), timeout=1) as client:
                    client.sendall(b'focus wrong-secret\n')
                    self.assertEqual(client.recv(16), b'')
                self.assertFalse(first.focus.is_set())
            finally: first.close()

    def test_existing_server_not_restarted(self):
        lab = Mock(); lab.running_server_url.return_value = 'http://127.0.0.1:8888/lab?token=test'
        with patch.object(m.subprocess, 'Popen') as spawn:
            url = m.wait_for_server(lab, Path('/runtime'), Path('/workspace'), threading.Event())
            self.assertTrue(url.startswith('http://127.0.0.1:'))
            spawn.assert_not_called()

    def test_stale_info_without_lock_does_not_block_new_owner(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / 'desktop-window.json').write_text('{}')
            owner = m.WindowOwner(root)
            try:
                self.assertTrue(owner.acquire()); owner.listen()
                self.assertIn('token', json.loads(owner.info.read_text()))
            finally: owner.close()

if __name__ == '__main__': unittest.main()
