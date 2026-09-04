import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('installer', ROOT / 'installer/install.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class InstallerTests(unittest.TestCase):
    def test_core_routes(self):
        p = Path('/package with spaces')
        self.assertEqual(m.core_payload(p, 'Core'), p / 'payload')
        self.assertEqual(m.core_payload(p, 'Complete'), p / 'Packages/ManSci-Core/payload')
        self.assertEqual(m.core_payload(p, 'Lab'), p / 'payload/core/payload')

    def test_declined_terms_stop(self):
        with patch('builtins.input', return_value='n'):
            with self.assertRaises(RuntimeError): m.consent('Accept?')

    def test_existing_model_not_pulled(self):
        with patch.object(m, 'data_from_ollama', return_value={'models':[{'name':m.MODEL}]}), patch.object(m, 'run') as run:
            m.prepare_model('/ollama')
            run.assert_not_called()

    def test_download_verified(self):
        responses = [{'models':[]}, {'models':[]}, {'models':[{'name':m.MODEL}]}]
        with patch.object(m, 'data_from_ollama', side_effect=responses), patch.object(m, 'run') as run:
            m.prepare_model('/ollama')
            run.assert_called_once_with(['/ollama', 'pull', m.MODEL])

    def test_failed_download_propagates(self):
        with patch.object(m, 'data_from_ollama', return_value={'models':[]}), patch.object(m, 'run', side_effect=RuntimeError('network failed')):
            with self.assertRaises(RuntimeError): m.prepare_model('/ollama')

    def test_shortcut_uses_expanded_windows_path(self):
        text = (ROOT / 'installer/shortcut.ps1').read_text()
        self.assertIn("Join-Path $env:WINDIR 'System32\\wscript.exe'", text)
        self.assertNotIn("'$env:WINDIR", text)
        self.assertIn('$check.TargetPath', text)

    def test_all_entrypoints_pause(self):
        for kind in ('Core','Spyder','Lab','VS-Code','Complete'):
            p = ROOT / 'distributions' / ('ManSci-' + kind)
            prefix = 'Install-All' if kind == 'Complete' else 'Install'
            self.assertIn('pause', (p / (prefix + '-Windows.bat')).read_text())
            self.assertIn('Press Return', (p / (prefix + '-Mac.command')).read_text())

    def test_windows_launcher_uses_permanent_paths_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix='ManSci test ') as directory:
            root = Path(directory)
            with patch.object(m, 'support', return_value=root), patch.object(m, 'os', SimpleNamespace(name='nt')), patch.object(m, 'run') as run:
                m.install_tool('Spyder', ROOT / 'distributions/ManSci-Spyder/payload',
                               'C:\\Users\\Test User\\miniconda3\\Scripts\\conda.exe', '', '', '')
            text = (root / 'Spyder/launch.bat').read_text()
            self.assertIn('"C:\\Users\\Test User\\miniconda3\\Scripts\\conda.exe" run', text)
            self.assertIn('"%~dp0launch.py"', text)
            args = run.call_args.args[0]
            self.assertIn(root / 'Spyder/launch.bat', args)
            self.assertTrue((root / 'Spyder/spyder.ico').is_file())

    def test_mac_reinstall_preserves_real_app_bundles(self):
        import plistlib
        with tempfile.TemporaryDirectory(prefix='ManSci test ') as directory:
            home = Path(directory)
            with patch.object(m, 'support', return_value=home / 'support'), patch.object(m.Path, 'home', return_value=home), patch.object(m, 'run'):
                for _ in range(2):
                    m.install_tool('Spyder', ROOT / 'distributions/ManSci-Spyder/payload',
                                   str(home / 'miniconda3/bin/conda'), '', '', '')
            for parent in ('Desktop', 'Applications'):
                app = home / parent / 'ManSci Spyder.app'
                self.assertFalse(app.is_symlink())
                with (app / 'Contents/Info.plist').open('rb') as f:
                    self.assertEqual(plistlib.load(f)['CFBundleIconFile'], 'spyder.icns')
                self.assertIn(str(home / 'support/Spyder/launch.py'), (app / 'Contents/MacOS/launch').read_text())

if __name__ == '__main__': unittest.main()
