import ast
from pathlib import Path
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "distributions/ManSci-Lab/payload"


class StudentLabPersonaTests(unittest.TestCase):
    def test_qwen_supports_both_persona_manager_chat_interfaces(self):
        source = (PAYLOAD / "personas/qwen_local_persona.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        helper = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_chat_document")
        namespace = {}
        exec(compile(ast.Module(body=[helper], type_ignores=[]), "qwen_helper", "exec"), namespace)
        current = object()
        former = object()
        self.assertIs(namespace["_chat_document"](SimpleNamespace(chat=current)), current)
        self.assertIs(namespace["_chat_document"](SimpleNamespace(ychat=former)), former)
        self.assertIn("chat_document.get_messages()", source)
        self.assertIn("MAX_HISTORY_MESSAGES = 12", source)
        self.assertIn("MAX_HISTORY_CHARACTERS = 12_000", source)

    def test_student_and_staff_pin_the_same_persona_manager_stack(self):
        student = (PAYLOAD / "requirements-student.txt").read_text(encoding="utf-8")
        staff = (
            ROOT / "distributions/ManSci-Staff-Lab/payload/requirements-staff.txt"
        ).read_text(encoding="utf-8")
        for requirement in (
            "jupyter-ai==3.2.0",
            "jupyter-ai-litellm==0.1.0",
            "jupyter-ai-router==0.1.1",
            "jupyter-ai-persona-manager==0.2.0",
            "jupyterlab-chat==0.25.0",
        ):
            self.assertIn(requirement, student)
            self.assertIn(requirement, staff)

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
