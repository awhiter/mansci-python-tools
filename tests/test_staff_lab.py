import ast
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / 'distributions/ManSci-Staff-Lab/payload'

keyring = types.ModuleType('keyring')
keyring.get_password = lambda *args: None
keyring.set_password = lambda *args: None
keyring.delete_password = lambda *args: None
errors = types.ModuleType('keyring.errors')
class KeyringError(Exception): pass
class PasswordDeleteError(Exception): pass
errors.KeyringError = KeyringError
errors.PasswordDeleteError = PasswordDeleteError
keyring.errors = errors
sys.modules.setdefault('keyring', keyring)
sys.modules.setdefault('keyring.errors', errors)
spec = importlib.util.spec_from_file_location('staff_lab_tested', PAYLOAD / 'staff_lab.py')
staff = importlib.util.module_from_spec(spec); spec.loader.exec_module(staff)

class StaffLabTests(unittest.TestCase):
    def test_sources_parse_and_native_window_imports_staff_module(self):
        for name in ('staff_lab.py', 'lab_window.py', 'mansci_jupyter_ai_guard.py'):
            ast.parse((PAYLOAD / name).read_text(encoding='utf-8'))
        window = (PAYLOAD / 'lab_window.py').read_text(encoding='utf-8')
        self.assertIn('import staff_lab as lab', window)
        self.assertNotIn('import student_lab as lab', window)
        self.assertIn('env.update(lab.server_environment())', window)

    def test_current_vm_compatible_ai_stack_and_learning_persona_are_included(self):
        requirements = (PAYLOAD / 'requirements-staff.txt').read_text()
        for package in ('jupyter-ai==3.2.0', 'jupyter-ai-tools==0.7.0',
                        'jupyter-server-mcp==0.3.0', 'jupyterlab-commands-toolkit==0.2.0'):
            self.assertIn(package, requirements)
        persona = (PAYLOAD / 'personas/mansci_learning_persona.py').read_text()
        ast.parse(persona)
        self.assertIn('ManSci Learning Assistant', persona)
        self.assertIn('test edge cases', persona)
        self.assertIn('if self.get_mcp_settings() is None:', persona)
        self.assertIn('message_with_attachment_instruction(message)', persona)
        config = (PAYLOAD / 'jupyter-config/jupyter_server_config.py').read_text()
        self.assertIn('mansci_learning_persona::ManSciLearningAssistantPersona', config)
        self.assertIn('c.PersonaManager.builtin_mcp_servers = []', config)
        self.assertIn('{"jupyter_server_mcp": False}', config)

    def test_upgrade_stops_only_authenticated_private_local_server(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = root / 'jupyter-runtime'; runtime.mkdir()
            (runtime / 'jpserver-1.json').write_text(json.dumps({
                'url': 'http://127.0.0.1:9999/', 'token': 'private token'
            }))
            response = MagicMock(); response.__enter__.return_value.status = 200
            with patch.object(staff, 'data_dir', return_value=root), \
                 patch.object(staff, 'urlopen', return_value=response) as opened, \
                 patch.object(staff.time, 'sleep'):
                staff.stop_private_server()
            request = opened.call_args.args[0]
            self.assertEqual(request.method, 'POST')
            self.assertEqual(request.full_url, 'http://127.0.0.1:9999/api/shutdown?token=private%20token')

    def test_shared_home_pointer_is_honoured(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory); chosen = home / 'Chosen Code'
            pointer = home / 'Documents/ManSci Code Home.txt'
            pointer.parent.mkdir(); pointer.write_text(str(chosen) + '\n')
            with patch.object(staff.Path, 'home', return_value=home):
                self.assertEqual(staff.documents_dir(), chosen)

    def test_server_environment_contains_key_only_in_memory(self):
        settings = {'endpoint':'https://example.openai.azure.com', 'deployment':'gpt-4.1', 'api_version':'2024-10-21'}
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(staff, 'data_dir', return_value=Path(directory)), \
             patch.object(staff, 'configure', return_value=(settings, 'SECRET-ONLY-IN-MEMORY')):
            env = staff.server_environment()
            self.assertEqual(env['AZURE_OPENAI_API_KEY'], 'SECRET-ONLY-IN-MEMORY')
            saved = json.loads((Path(directory) / 'jupyter-data/jupyter_ai/config.json').read_text())
            self.assertNotIn('SECRET-ONLY-IN-MEMORY', json.dumps(saved))
            self.assertEqual(saved['api_keys'], {})

    def test_staff_package_contains_no_specific_azure_resource_or_key(self):
        for file in PAYLOAD.rglob('*'):
            if file.is_file() and '__pycache__' not in file.parts and file.suffix != '.pyc':
                text = file.read_text(encoding='utf-8', errors='ignore')
                self.assertNotIn('cognitiveservices.azure.com', text)

if __name__ == '__main__': unittest.main()
