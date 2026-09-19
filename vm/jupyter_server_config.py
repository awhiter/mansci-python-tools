"""ManSci VM Jupyter Server settings."""

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import shutil

c = get_config()  # noqa: F821 - supplied by Jupyter's configuration loader

_TEACHING_ROOT = Path("/srv/mansci/teaching")
_BACKUP_ROOT = Path("/srv/mansci/teaching-backups")


def _mansci_backup_before_save(model, path, contents_manager, **kwargs):
    """Preserve the current central file before Jupyter replaces it."""
    try:
        target = (Path(contents_manager.root_dir) / path).resolve()
        relative = target.relative_to(_TEACHING_ROOT.resolve())
    except (OSError, ValueError):
        return
    if not target.is_file() or len(relative.parts) < 2:
        return

    module_backup_root = _BACKUP_ROOT / relative.parts[0]
    if not module_backup_root.is_dir():
        contents_manager.log.warning(
            "No ManSci backup directory exists for central file %s", target
        )
        return

    relative_in_module = Path(*relative.parts[1:])
    version_dir = module_backup_root / "versions" / relative_in_module.parent / target.name
    version_dir.mkdir(parents=True, exist_ok=True)

    current_hash = hashlib.sha256(target.read_bytes()).hexdigest()
    previous = sorted(version_dir.glob(f"*-{target.name}"))
    if previous and hashlib.sha256(previous[-1].read_bytes()).hexdigest() == current_hash:
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = version_dir / f"{timestamp}-{target.name}"
    shutil.copy2(target, backup)
    contents_manager.log.info("Preserved central teaching file as %s", backup)

    versions = sorted(version_dir.glob(f"*-{target.name}"))
    for expired in versions[:-50]:
        expired.unlink()


c.FileContentsManager.pre_save_hook = _mansci_backup_before_save
