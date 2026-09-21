"""Reject generated decks that have lost the supplied UCL template structure."""
from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZipFile


def validate(path: Path) -> None:
    with ZipFile(path) as archive:
        names = archive.namelist()
        layouts = [name for name in names if name.startswith("ppt/slideLayouts/") and name.endswith(".xml")]
        masters = [name for name in names if name.startswith("ppt/slideMasters/") and name.endswith(".xml")]
        xml = "".join(
            archive.read(name).decode("utf-8", "ignore")
            for name in names
            if name.endswith(".xml")
        )
    failures = []
    if len(layouts) < 42:
        failures.append(f"only {len(layouts)} slide layouts (expected at least 42)")
    if not masters:
        failures.append("no slide master")
    if "UCL Sans" not in xml:
        failures.append("UCL Sans theme/font references are absent")
    if failures:
        raise SystemExit(f"{path}: UCL template validation failed: " + "; ".join(failures))
    print(f"PASS: {path} retains the UCL template ({len(layouts)} layouts, {len(masters)} master).")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("decks", nargs="+", type=Path)
    args = parser.parse_args()
    for deck in args.decks:
        validate(deck)


if __name__ == "__main__":
    main()
