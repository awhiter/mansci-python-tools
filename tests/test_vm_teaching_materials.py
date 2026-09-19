from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_teaching_notebooks_are_protected_by_labextension():
    source = (ROOT / "vm/mansci-copy-to-my-work/src/index.ts").read_text()
    assert "Teaching Materials/" in source
    assert "model.readOnly = true" in source
    assert "canStart: false" in source
    assert "shouldStart: false" in source
    assert "Copy to My Work" in source
    assert "isModuleLead()" in source
    assert "endsWith('_lead')" in source
    protected = source.split("async function protectTeachingNotebook", 1)[1]
    assert protected.index("canStart: false") < protected.index("await panel.context.ready")
    assert "prepareEditableCopy(copied)" in source
    assert "await sessionContext.session.kernel.info" in source


def test_central_teaching_saves_create_versioned_backups():
    config = (ROOT / "vm/jupyter_server_config.py").read_text()
    assert "c.FileContentsManager.pre_save_hook = _mansci_backup_before_save" in config
    assert 'Path("/srv/mansci/teaching-backups")' in config
    assert "c.YRoomManager.auto_free_interval" not in config


def test_realtime_document_providers_are_disabled_and_locked():
    script = (ROOT / "vm/disable-rtc-document-providers.sh").read_text()
    for plugin in ("ynotebook", "yfile"):
        assert f"@jupyter/docprovider-extension:{plugin}" in script
    assert "labextension disable" in script
    assert "labextension lock" in script
    assert '"@jupyterlab/notebook-extension:cell-executor"' in script
    assert 'data.setdefault("disabledExtensions", {})[executor] = False' in script
    assert 'data.setdefault("lockedExtensions", {})[executor] = True' in script
    assert "@jupyter-ai-contrib/server-documents:server-cell-executor" in script


def test_persona_describes_enforced_copy_workflow():
    persona = (ROOT / "vm/mansci-learning-assistant/persona.py").read_text()
    assert "Notebooks opened there are view-only" in persona
    assert "cannot edit cells, run cells, or start a kernel" in persona


def test_installer_keeps_extension_backups_outside_scan_path():
    installer = (ROOT / "vm/mansci-copy-to-my-work/install-vm.sh").read_text()
    assert "/var/backups/mansci-jupyterlab-extensions" in installer
    assert "LEGACY_BACKUP" in installer
