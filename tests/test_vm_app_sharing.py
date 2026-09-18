import ast
import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "vm/mansci_tools.py"


class VmAppSharingTests(unittest.TestCase):
    def test_vm_sources_compile(self):
        for path in (RUNNER, ROOT / "vm/mansci-app-share/service.py"):
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_phone_url_preserves_shared_service_path(self):
        spec = importlib.util.spec_from_file_location("vm_mansci_tools", RUNNER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with patch.dict(os.environ, {
            "JUPYTERHUB_SERVICE_PREFIX": "/user/presenter/",
            "MANSCI_PUBLIC_BASE_URL": "https://example.test",
        }, clear=True):
            url = module._phone_url("/services/mansci-app-share/s/opaque/")
        self.assertEqual(
            url,
            "https://example.test/hub/login?next=%2Fservices%2Fmansci-app-share%2Fs%2Fopaque%2F",
        )

    def test_stop_instruction_is_self_contained(self):
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn("from mansci_tools import stop_app; stop_app", source)

    def test_local_core_is_not_changed_to_classroom_sharing(self):
        source = (ROOT / "distributions/ManSci-Core/payload/mansci_tools.py").read_text()
        self.assertNotIn("mansci-app-share", source)


if __name__ == "__main__":
    unittest.main()
