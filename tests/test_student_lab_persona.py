import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "distributions/ManSci-Lab/payload"


class StudentLabPersonaTests(unittest.TestCase):
    def test_qwen_uses_current_persona_manager_chat_interface(self):
        source = (PAYLOAD / "personas/qwen_local_persona.py").read_text(encoding="utf-8")
        ast.parse(source)
        self.assertIn("self.chat.get_messages()", source)
        self.assertNotIn("self.ychat", source)
        self.assertIn("MAX_HISTORY_MESSAGES = 12", source)
        self.assertIn("MAX_HISTORY_CHARACTERS = 12_000", source)

    def test_student_lab_registers_only_its_packaged_qwen_persona(self):
        guard = (PAYLOAD / "mansci_student_persona_guard.py").read_text(encoding="utf-8")
        config = (PAYLOAD / "jupyter-config/jupyter_server_config.py").read_text(encoding="utf-8")
        window = (PAYLOAD / "lab_window.py").read_text(encoding="utf-8")
        ast.parse(guard)
        ast.parse(config)
        self.assertIn('PersonaManager._ep_persona_classes = []', guard)
        self.assertIn('Path(__file__).resolve().parent / "personas"', guard)
        self.assertNotIn("get_dotjupyter_dir", guard)
        self.assertIn("install_student_persona_guard()", config)
        self.assertIn("qwen_local_persona::QwenLocalChatPersona", config)
        self.assertNotIn("install_local_persona(workspace)", window)

    def test_staff_lab_keeps_its_separate_persona_configuration(self):
        config = (
            ROOT / "distributions/ManSci-Staff-Lab/payload/jupyter-config/jupyter_server_config.py"
        ).read_text(encoding="utf-8")
        self.assertIn("mansci_learning_persona::ManSciLearningAssistantPersona", config)
        self.assertNotIn("mansci_student_persona_guard", config)


if __name__ == "__main__":
    unittest.main()
