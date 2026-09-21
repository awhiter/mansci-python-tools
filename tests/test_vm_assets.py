import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class VMAssetTests(unittest.TestCase):
    def test_enrol_command_has_authorised_read_only_reporting(self):
        wrapper = (ROOT / "vm/mansci-enrol/mansci-enrol").read_text()
        backend = (ROOT / "vm/mansci-enrol/mansci-enrol-backend").read_text()
        guide = (ROOT / "vm/mansci-enrol/README.md").read_text()
        for option in ("--list", "--count"):
            self.assertIn(option, wrapper)
            self.assertIn(option, backend)
            self.assertIn(option, guide)
        self.assertLess(backend.index("authorise(caller, module)"), backend.index('if len(sys.argv) == 3:'))
        ast.parse(backend)

    def test_vm_persona_requires_verification_and_no_fabricated_results(self):
        persona = (ROOT / "vm/mansci-learning-assistant/persona.py").read_text()
        ast.parse(persona)
        self.assertIn("Never invent a command", persona)
        self.assertIn("mansci-enrol MODULE --list", persona)
        self.assertIn("illustrative output as hypothetical", persona)
        self.assertIn("QR contains no credential", persona)
        self.assertIn("ModelConfiguration(current=None, options=[], settings=[])", persona)
        self.assertIn("Do not", persona)
        self.assertIn("Team_Project_Context.md", persona)
        self.assertIn("coordination evidence, not independent proof", persona)
        self.assertIn("Open With → Editor", persona)
        overrides = (ROOT / "vm/jupyterlab-overrides.json").read_text()
        self.assertEqual(__import__('json').loads(overrides)["@jupyterlab/docmanager-extension:plugin"]["defaultViewers"]["markdown"], "Markdown Preview")


if __name__ == "__main__":
    unittest.main()
