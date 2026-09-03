#!/usr/bin/env python3
"""Create and verify the shared Management Science teaching workspace."""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

CORE_VERSION = "2026.09.03.1"


def support_dir() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "ManagementScience"
    return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "ManagementScience"


def home_dir() -> Path:
    pointer = Path.home() / "Documents" / "ManSci Code Home.txt"
    default = Path.home() / "Documents" / "ManSci Code"
    if pointer.exists() and (value := pointer.read_text(encoding="utf-8").strip()):
        return Path(os.path.expandvars(value)).expanduser()
    pointer.parent.mkdir(parents=True, exist_ok=True)
    pointer.write_text(str(default) + "\n", encoding="utf-8")
    return default


def notebook() -> dict:
    return {
        "cells": [
            {"cell_type": "markdown", "id": "intro", "metadata": {}, "source": [
                "# Management Science Python test\n", "Run the cell below. It should report **PASS**."
            ]},
            {"cell_type": "code", "id": "test", "execution_count": None,
             "metadata": {}, "outputs": [], "source": [
                "import sys\n", "import numpy as np\n", "import pandas as pd\n",
                "import statsmodels.api as sm\n",
                "print('Interpreter:', sys.executable)\n",
                "print('PASS' if 'mansci-python' in sys.executable.lower() else 'FAIL')\n",
                "pd.DataFrame({'value': np.arange(1, 6)})\n"
             ]}
        ],
        "metadata": {"kernelspec": {"display_name": "Management Science Python",
            "language": "python", "name": "mansci-python"},
            "language_info": {"name": "python", "version": platform.python_version()}},
        "nbformat": 4, "nbformat_minor": 5
    }


def initialise() -> None:
    home = home_dir()
    home.mkdir(parents=True, exist_ok=True)
    files = {
        "README - Keep your work here.md": """# ManSci Code

Keep all Python scripts, notebooks, data files and coursework folders inside this **ManSci Code** folder.

ManSci Spyder, ManSci Lab and ManSci VS Code all open this same folder and use the same `mansci-python` environment. A program created in one tool can therefore be opened and run in either of the others.

You may organise your work into module and assignment subfolders. Do not save your only copy inside an installer, Downloads folder or temporary folder. Back up important work using the storage service recommended by your programme.
""",
        "test.py": """# %%
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm

print("Interpreter:", sys.executable)
print("Environment test:", "PASS" if "mansci-python" in sys.executable.lower() else "FAIL")

# %%
data = pd.DataFrame({"period": np.arange(1, 6), "demand": [12, 15, 14, 18, 20]})
print(data)
print("Average demand:", data["demand"].mean())
""",
    }
    for name, content in files.items():
        target = home / name
        if not target.exists():
            target.write_text(content, encoding="utf-8")
    nb = home / "test.ipynb"
    if not nb.exists():
        nb.write_text(json.dumps(notebook(), indent=2) + "\n", encoding="utf-8")
    marker = support_dir() / "Core" / "version.txt"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(CORE_VERSION + "\n", encoding="utf-8")
    print(f"Shared coding home: {home}")


def register_kernel() -> None:
    subprocess.run([sys.executable, "-m", "ipykernel", "install", "--user", "--name",
                    "mansci-python", "--display-name", "Management Science Python"], check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("initialise", "check"))
    args = parser.parse_args()
    if args.action == "initialise":
        register_kernel()
        initialise()
        return 0
    modules = ("numpy", "pandas", "scipy", "statsmodels", "matplotlib", "sklearn", "sympy",
               "openpyxl", "networkx", "seaborn", "requests", "spyder", "jupyterlab")
    failed = False
    print("Python:", sys.executable)
    print("Version:", platform.python_version())
    for name in modules:
        ok = __import__(name) is not None
        print(f"{'PASS' if ok else 'FAIL'}: {name}")
        failed |= not ok
    print("Coding home:", home_dir())
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
