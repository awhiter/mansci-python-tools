from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_teaching_notebooks_are_protected_by_labextension():
    source = (ROOT / "vm/mansci-copy-to-my-work/src/index.ts").read_text()
    assert "Teaching Materials/" in source
    assert "model.readOnly = true" in source
    assert "canStart: false" in source
    assert "shouldStart: false" in source
    assert "Copy to My Work" in source


def test_inactive_collaboration_rooms_are_released_promptly():
    config = (ROOT / "vm/jupyter_server_config.py").read_text()
    assert "c.YRoomManager.auto_free_interval = 15" in config


def test_persona_describes_enforced_copy_workflow():
    persona = (ROOT / "vm/mansci-learning-assistant/persona.py").read_text()
    assert "Notebooks opened there are view-only" in persona
    assert "cannot edit cells, run cells, or start a kernel" in persona


def test_installer_keeps_extension_backups_outside_scan_path():
    installer = (ROOT / "vm/mansci-copy-to-my-work/install-vm.sh").read_text()
    assert "/var/backups/mansci-jupyterlab-extensions" in installer
    assert "LEGACY_BACKUP" in installer
