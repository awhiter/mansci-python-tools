from __future__ import annotations

import os
import shutil
from pathlib import Path, PurePosixPath

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado.web

TEACHING = "Teaching Materials"
MY_WORK = "My Work"


class CopyError(ValueError):
    pass


def destination_for(source: str) -> PurePosixPath:
    path = PurePosixPath(source)
    parts = path.parts
    if path.is_absolute() or ".." in parts or len(parts) < 3 or parts[0] != TEACHING:
        raise CopyError("Only files and folders beneath Teaching Materials can be copied.")
    module = parts[1]
    if not module or module in {".", ".."}:
        raise CopyError("The selected item is not inside a valid module folder.")
    return PurePosixPath(MY_WORK, module, *parts[2:])


def copy_item(root: Path, source: str) -> Path:
    relative_source = PurePosixPath(source)
    relative_destination = destination_for(source)
    root = root.resolve()
    source_path = root.joinpath(*relative_source.parts)
    destination = root.joinpath(*relative_destination.parts)
    teaching_module = root / TEACHING / relative_source.parts[1]
    work_module = root / MY_WORK / relative_source.parts[1]

    if not source_path.exists():
        raise CopyError("The selected file or folder no longer exists.")
    try:
        source_path.resolve(strict=True).relative_to(teaching_module.resolve(strict=True))
    except (OSError, ValueError):
        raise CopyError("The selected item is not valid Teaching Materials.")
    try:
        work_module.resolve(strict=True).relative_to((root / MY_WORK).resolve(strict=True))
    except (OSError, ValueError):
        raise CopyError("The corresponding module folder does not exist in My Work.")
    if os.path.lexists(destination):
        raise FileExistsError(
            f"{relative_destination.name} already exists in My Work. "
            "Your existing work has not been changed. If you still want a copy "
            "of the current version from Teaching Materials, first rename your "
            "existing file or folder in My Work, then try Copy to My Work again."
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    if source_path.is_dir():
        shutil.copytree(source_path, destination, symlinks=False)
    else:
        shutil.copy2(source_path, destination)
    return destination


class CopyToMyWorkHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        body = self.get_json_body() or {}
        try:
            destination = copy_item(Path(self.contents_manager.root_dir), body.get("source", ""))
        except FileExistsError as exc:
            raise tornado.web.HTTPError(409, reason=str(exc))
        except (CopyError, OSError) as exc:
            raise tornado.web.HTTPError(400, reason=str(exc))
        relative = destination.relative_to(Path(self.contents_manager.root_dir).resolve())
        self.finish({
            "destination": relative.as_posix(),
            "message": f"Copied to {relative.as_posix()}."
        })


def setup_handlers(web_app):
    route = url_path_join(web_app.settings["base_url"], "mansci-copy-to-my-work")
    web_app.add_handlers(".*$", [(route, CopyToMyWorkHandler)])
