import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

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

if __name__ == "__main__": unittest.main()
