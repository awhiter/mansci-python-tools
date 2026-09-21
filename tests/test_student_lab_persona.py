import ast
import json
from pathlib import Path
import re
from types import SimpleNamespace
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "distributions/ManSci-Lab/payload"


class StudentLabPersonaTests(unittest.TestCase):
    def _qwen_helpers(self):
        source = (PAYLOAD / "personas/qwen_local_persona.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        names = {
            "_chat_document", "_workspace_root", "_safe_workspace_path",
            "_notebook_text", "_read_workspace_text", "_referenced_paths",
            "_message_content",
        }
        nodes = [
            node for node in tree.body
            if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names)
            or (isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id in {"SUPPORTED_TEXT_SUFFIXES", "FILE_REFERENCE_RE"}
                for target in node.targets
            ))
        ]
        namespace = {"Path": Path, "json": json, "re": re}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), "qwen_helpers", "exec"), namespace)
        return namespace

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

    def test_qwen_adds_saved_attachment_content(self):
        helpers = self._qwen_helpers()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "party.py").write_text("print('party')\n", encoding="utf-8")
            attachment = SimpleNamespace(value="party.py")
            chat = SimpleNamespace(get_attachments=lambda: {"a1": attachment})
            persona = SimpleNamespace(parent=SimpleNamespace(root_dir=directory), chat=chat)
            message = SimpleNamespace(body="Explain this", attachments=["a1"])
            content = helpers["_message_content"](persona, message, 12_000)
            self.assertIn("Saved ManSci workspace file: party.py", content)
            self.assertIn("print('party')", content)

    def test_qwen_resolves_unambiguous_filename_reference_and_notebook_sources(self):
        helpers = self._qwen_helpers()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / "project"
            nested.mkdir()
            (nested / "party.py").write_text("x = 3\n", encoding="utf-8")
            paths, notices = helpers["_referenced_paths"](root, "Please explain party.py")
            self.assertEqual(paths, [nested / "party.py"])
            self.assertEqual(notices, [])
            notebook = root / "lesson.ipynb"
            notebook.write_text(json.dumps({"cells": [
                {"cell_type": "markdown", "source": ["# Lesson\n"]},
                {"cell_type": "code", "source": ["print(2)\n"]},
            ]}), encoding="utf-8")
            text, error = helpers["_read_workspace_text"](root, notebook, 8_000)
            self.assertIsNone(error)
            self.assertIn("markdown cell 1", text)
            self.assertIn("print(2)", text)

    def test_qwen_rejects_paths_outside_workspace(self):
        helpers = self._qwen_helpers()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with self.assertRaisesRegex(ValueError, "outside"):
                helpers["_safe_workspace_path"](root, "../secret.txt")

    def test_qwen_uses_matching_compact_local_only_context(self):
        student = (PAYLOAD / "personas/qwen_local_context.md").read_text(encoding="utf-8")
        staff = (
            ROOT / "distributions/ManSci-Staff-Lab/payload/personas/qwen_local_context.md"
        ).read_text(encoding="utf-8")
        persona = (PAYLOAD / "personas/qwen_local_persona.py").read_text(encoding="utf-8")
        self.assertEqual(student, staff)
        self.assertIn("_local_context()", persona)
        for expected in (
            "Python 3.13", "Documents/ManSci Code", "streamlit", "flask",
            "pandas", "sklearn", "run_app", "stop_app", "mansci-python",
        ):
            self.assertIn(expected, student)
        for vm_only in ("Team Exchange", "JupyterHub", "classroom phone", "Teaching Materials"):
            self.assertNotIn(vm_only, student)
        self.assertLess(len(student), 6_000)

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
