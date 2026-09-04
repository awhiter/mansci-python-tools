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
    def test_spyder_preserves_windowless_host_identity(self):
        spec = importlib.util.spec_from_file_location('managed_launch', ROOT / 'installer/launch.py')
        launch = importlib.util.module_from_spec(spec); spec.loader.exec_module(launch)
        console = r'C:\Users\Student\env\python.exe'
        windowless = r'C:\Users\Student\env\pythonw.exe'
        self.assertEqual(launch.runtime_executable('Spyder', console, windowless), windowless)
        for kind in ('Lab', 'VS-Code'):
            self.assertEqual(launch.runtime_executable(kind, console, windowless), console)
        self.assertEqual(launch.runtime_executable('Spyder', '/env/bin/python', '/env/bin/python'), '/env/bin/python')

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

    def test_shortcut_targets_executable_and_does_not_pin(self):
        text = (ROOT / 'installer/shortcut.ps1').read_text()
        self.assertIn('$target = $Executable', text)
        self.assertIn("GetFolderPath('Programs')", text)
        self.assertNotIn("'$env:WINDIR", text)
        self.assertIn('$check.TargetPath', text)
        self.assertIn('ManSci VS Code Check.lnk', text)
        self.assertIn('Remove-Item -LiteralPath $oldPath', text)
        for forbidden in ('InvokeVerb', 'Taskband', 'taskbarpin', 'LayoutModification'):
            self.assertNotIn(forbidden, text)

    def test_all_entrypoints_pause(self):
        for kind in ('Core','Spyder','Lab','VS-Code','Complete'):
            p = ROOT / 'distributions' / ('ManSci-' + kind)
            prefix = 'Install-All' if kind == 'Complete' else 'Install'
            self.assertIn('pause', (p / (prefix + '-Windows.bat')).read_text())
            self.assertIn('Press Return', (p / (prefix + '-Mac.command')).read_text())

    def test_windows_help_is_versioned_and_uses_quoted_local_html(self):
        with tempfile.TemporaryDirectory(prefix='ManSci help ') as directory:
            root = Path(directory)
            fake_os = SimpleNamespace(name='nt', environ={'WINDIR': 'C:\\Windows'})
            with patch.object(m, 'support', return_value=root), patch.object(m, 'os', fake_os), patch.object(m, 'run') as run:
                m.install_help(ROOT / 'distributions/ManSci-Core/payload')
            html = (root / 'Core/ManSci-Help.html').read_text()
            self.assertIn(m.VERSION, html)
            self.assertNotIn('{{VERSION}}', html)
            args = run.call_args.args[0]
            self.assertIn('ManSci Help', args)
            self.assertEqual(args[args.index('-Arguments') + 1], '"' + str(root / 'Core/ManSci-Help.html') + '"')

    def test_mac_help_is_a_fresh_signed_app_with_offline_target(self):
        with tempfile.TemporaryDirectory(prefix='ManSci help ') as directory:
            home = Path(directory); root = home / 'support'
            for parent in ('Desktop', 'Applications'):
                for name in ('ManSci Check.app', 'ManSci VS Code Check.app'):
                    old = home / parent / name
                    (old / 'Contents').mkdir(parents=True)
            with patch.object(m, 'support', return_value=root), patch.object(m.Path, 'home', return_value=home), patch.object(m, 'run') as run:
                m.install_help(ROOT / 'distributions/ManSci-Core/payload')
            for parent in ('Desktop', 'Applications'):
                app = home / parent / 'ManSci Help.app'
                launch = (app / 'Contents/MacOS/launch').read_text()
                self.assertIn('/usr/bin/open', launch)
                self.assertIn(str(root / 'Core/ManSci-Help.html'), launch)
                self.assertFalse((home / parent / 'ManSci Check.app').exists())
                self.assertFalse((home / parent / 'ManSci VS Code Check.app').exists())
            self.assertTrue(any(call.args[0][0] == 'codesign' for call in run.call_args_list))

    def test_windows_launcher_uses_permanent_paths_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix='ManSci test ') as directory:
            root = Path(directory)
            python = root / 'env/python.exe'
            python.parent.mkdir()
            python.with_name('pythonw.exe').touch()
            with patch.object(m, 'support', return_value=root), patch.object(m, 'os', SimpleNamespace(name='nt')), patch.object(m, 'run', return_value='{}') as run:
                m.install_tool('Spyder', ROOT / 'distributions/ManSci-Spyder/payload',
                               'C:\\Users\\Test User\\miniconda3\\Scripts\\conda.exe', str(python), '', '')
            self.assertFalse((root / 'Spyder/launch.bat').exists())
            args = run.call_args.args[0]
            self.assertIn(root / 'Spyder/ManSci Spyder.exe', args)
            runtime = (root / 'Spyder/launcher-runtime.txt').read_text().splitlines()
            self.assertEqual(runtime, [str(python.with_name('pythonw.exe')), str(root / 'Spyder/launch.py')])
            self.assertTrue(any('build-windows-launcher.ps1' in str(call.args[0]) for call in run.call_args_list))
            self.assertTrue((root / 'Spyder/spyder.ico').is_file())
            window = (root / 'Spyder/window-runtime.txt').read_text().splitlines()
            self.assertEqual(window, ['Spyder', 'uk.ac.ucl.mansci.Spyder', '',
                                     str(root / 'Spyder/spyder.ico'), 'ManSci Spyder'])
            self.assertEqual(args[args.index('-AppId') + 1], window[1])
            source = (ROOT / 'installer/WindowsLauncher.cs').read_text()
            self.assertIn('window[0] == "Spyder"', source)
            self.assertIn('if (managedWindow)', source)

    def test_compiled_launcher_is_windowless_and_has_icon(self):
        build = (ROOT / 'installer/build-windows-launcher.ps1').read_text()
        source = (ROOT / 'installer/WindowsLauncher.cs').read_text()
        self.assertIn('/target:winexe', build)
        self.assertIn('/win32icon:$Icon', build)
        self.assertIn('start.CreateNoWindow = true', source)
        self.assertIn('child.WaitForExit()', source)

    def test_mac_reinstall_preserves_real_app_bundles(self):
        import plistlib
        with tempfile.TemporaryDirectory(prefix='ManSci test ') as directory:
            home = Path(directory)
            with patch.object(m, 'support', return_value=home / 'support'), patch.object(m.Path, 'home', return_value=home), patch.object(m, 'run', return_value='{}') as run:
                for _ in range(2):
                    m.install_tool('Spyder', ROOT / 'distributions/ManSci-Spyder/payload',
                                   str(home / 'miniconda3/bin/conda'), str(home / 'env/bin/python'), '', '')
            for parent in ('Desktop', 'Applications'):
                app = home / parent / 'ManSci Spyder.app'
                self.assertFalse(app.is_symlink())
                with (app / 'Contents/Info.plist').open('rb') as f:
                    self.assertEqual(plistlib.load(f)['CFBundleIconFile'], 'spyder.icns')
                self.assertIn(str(home / 'support/Spyder/launch.py'), (app / 'Contents/MacOS/launch').read_text())
                self.assertNotIn('conda', (app / 'Contents/MacOS/launch').read_text())
            calls = [call.args[0] for call in run.call_args_list]
            clean = next(i for i, args in enumerate(calls) if args[:2] == ['/usr/bin/xattr', '-cr'])
            sign = next(i for i, args in enumerate(calls) if args and args[0] == 'codesign')
            self.assertLess(clean, sign)
            self.assertNotIn('/Desktop/', str(calls[clean][-1]))
            self.assertNotIn('/Desktop/', str(calls[sign][-1]))

    def test_lab_browser_url_and_no_process_signal(self):
        spec = importlib.util.spec_from_file_location('student_lab', ROOT / 'distributions/ManSci-Lab/payload/student_lab.py')
        lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
        from unittest.mock import MagicMock
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'jpserver-123.json').write_text(json.dumps({'pid':123,'root_dir':directory,'url':'http://127.0.0.1:8888/','token':'test'}))
            response = MagicMock(); response.__enter__.return_value.status = 200
            with patch.object(lab, 'urlopen', return_value=response), patch.object(lab.os, 'kill') as kill, patch.object(lab.webbrowser, 'open') as browser:
                self.assertTrue(lab.open_existing_server(root, root))
                kill.assert_not_called()
                browser.assert_called_once_with('http://127.0.0.1:8888/lab?token=test')
        config = (ROOT / 'distributions/ManSci-Lab/payload/jupyter-config/jupyter_server_config.py').read_text()
        self.assertIn('use_redirect_file = False', config)

if __name__ == '__main__': unittest.main()
