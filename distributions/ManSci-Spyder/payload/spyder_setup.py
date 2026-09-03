#!/usr/bin/env python3
"""Install stable, isolated ManSci Spyder launch support."""
import configparser
import os
import shutil
import sys
from pathlib import Path


def support() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "ManagementScience" / "Spyder"
    return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "ManagementScience" / "Spyder"


def home() -> Path:
    pointer = Path.home() / "Documents" / "ManSci Code Home.txt"
    if pointer.exists() and (value := pointer.read_text(encoding="utf-8").strip()):
        return Path(os.path.expandvars(value)).expanduser()
    return Path.home() / "Documents" / "ManSci Code"


def main() -> None:
    root = support()
    root.mkdir(parents=True, exist_ok=True)
    conf = root / "config" / "spyder.ini"
    conf.parent.mkdir(parents=True, exist_ok=True)
    parser = configparser.ConfigParser(interpolation=None)
    if conf.exists():
        parser.read(conf, encoding="utf-8")
    if not parser.has_section("appearance"):
        parser.add_section("appearance")
    parser.set("appearance", "ui_theme", "light")
    parser.set("appearance", "selected", "spyder")
    if not parser.has_section("workingdir"):
        parser.add_section("workingdir")
    coding_home = str(home())
    parser.set("workingdir", "startup/use_project_or_home_directory", "False")
    parser.set("workingdir", "startup/use_fixed_directory", "True")
    parser.set("workingdir", "startup/fixed_directory", coding_home)
    parser.set("workingdir", "console/use_project_or_home_directory", "False")
    parser.set("workingdir", "console/use_cwd", "True")
    parser.set("workingdir", "console/use_fixed_directory", "False")
    parser.set("workingdir", "history", repr([coding_home]))
    with conf.open("w", encoding="utf-8") as handle:
        parser.write(handle)
    home().mkdir(parents=True, exist_ok=True)
    print(f"Spyder home: {coding_home}")
    print("Spyder theme: Light; syntax highlighting: Spyder")


if __name__ == "__main__":
    main()
