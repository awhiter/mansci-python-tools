import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("mansci_tools_tested", ROOT / "distributions/ManSci-Core/payload/mansci_tools.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class ManSciToolsTests(unittest.TestCase):
    def test_resolve_and_run_script_from_project_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); project = root / "Project"; project.mkdir()
            (project / "value.txt").write_text("42")
            script = project / "app.py"
            script.write_text("from pathlib import Path\nRESULT = Path('value.txt').read_text()\n")
            old = Path.cwd(); os.chdir(root)
            try:
                self.assertEqual(m.resolve_path("Project/app.py"), script.resolve())
                self.assertEqual(m.run_script("Project/app.py")["RESULT"], "42")
            finally:
                os.chdir(old)

    def test_missing_file_has_student_message(self):
        with tempfile.TemporaryDirectory() as directory:
            old = Path.cwd(); os.chdir(directory)
            try:
                with self.assertRaisesRegex(FileNotFoundError, "Save the file"):
                    m.resolve_path("missing.py")
            finally:
                os.chdir(old)

    def test_proxy_url_uses_hub_prefix(self):
        old = os.environ.get("JUPYTERHUB_SERVICE_PREFIX")
        os.environ["JUPYTERHUB_SERVICE_PREFIX"] = "/user/student1/"
        try:
            self.assertEqual(m._url(8123), "/user/student1/proxy/8123/")
        finally:
            if old is None: os.environ.pop("JUPYTERHUB_SERVICE_PREFIX", None)
            else: os.environ["JUPYTERHUB_SERVICE_PREFIX"] = old

    def test_named_frameworks_are_required_by_the_installer(self):
        installer = (ROOT / "installer/install.py").read_text()
        for module in ("streamlit", "gradio", "dash", "flask"):
            self.assertIn(f"'{module}'", installer)
            self.assertEqual(m.APP_MODULES[module], module)

    def test_flask_command_uses_allocated_port_without_debug_reloader(self):
        command = m._app_command(Path("party_flask.py"), "flask", 50229)
        self.assertEqual(command[:4], [m.sys.executable, "-m", "flask", "--app"])
        self.assertIn("50229", command)
        self.assertIn("--no-debugger", command)
        self.assertIn("--no-reload", command)

    def test_startup_timeout_raises_and_does_not_return_a_link(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "server.py"; path.write_text("while True: pass\n")
            process = MagicMock(pid=1234)
            process.poll.return_value = None
            process.wait.return_value = 0
            old = Path.cwd(); os.chdir(directory)
            try:
                with patch.object(m.subprocess, "Popen", return_value=process), \
                     patch.object(m, "_free_port", return_value=54321), \
                     patch.object(m.time, "time", side_effect=[0, 13]):
                    with self.assertRaisesRegex(RuntimeError, "no app link was created"):
                        m.run_app("server.py", kind="python")
            finally:
                os.chdir(old)
            process.terminate.assert_called_once()

if __name__ == "__main__": unittest.main()
