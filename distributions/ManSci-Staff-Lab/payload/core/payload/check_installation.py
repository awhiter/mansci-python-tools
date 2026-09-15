"""Check the Management Science Python teaching environment."""

from __future__ import annotations

import importlib
import os
import platform
import shutil
import subprocess
import sys
from importlib import metadata


PACKAGES = {
    "Spyder": ("spyder", "spyder"),
    "JupyterLab": ("jupyterlab", "jupyterlab"),
    "IPython kernel": ("ipykernel", "ipykernel"),
    "NumPy": ("numpy", "numpy"),
    "pandas": ("pandas", "pandas"),
    "SciPy": ("scipy", "scipy"),
    "Statsmodels": ("statsmodels", "statsmodels"),
    "Matplotlib": ("matplotlib", "matplotlib"),
    "scikit-learn": ("sklearn", "scikit-learn"),
    "SymPy": ("sympy", "sympy"),
    "openpyxl": ("openpyxl", "openpyxl"),
    "NetworkX": ("networkx", "networkx"),
    "seaborn": ("seaborn", "seaborn"),
    "Requests": ("requests", "requests"),
}


def pass_fail(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def main() -> int:
    expected_name = "mansci-python"
    active_name = os.environ.get("CONDA_DEFAULT_ENV", "(not set)")
    prefix = os.environ.get("CONDA_PREFIX", "(not set)")
    python_ok = sys.version_info[:2] == (3, 13)
    env_ok = active_name == expected_name

    print("Management Science Python - Installation Check")
    print("=" * 50)
    print(f"Executable:       {sys.executable}")
    print(f"Conda environment:{active_name:>20}")
    print(f"Conda prefix:     {prefix}")
    print(f"Python version:   {platform.python_version()}")
    print()
    print(f"[{pass_fail(env_ok)}] Running in '{expected_name}'")
    print(f"[{pass_fail(python_ok)}] Python version is 3.13.x")
    print()
    print("Package versions")
    print("-" * 50)

    packages_ok = True
    for label, (module_name, distribution_name) in PACKAGES.items():
        try:
            importlib.import_module(module_name)
            version = metadata.version(distribution_name)
            print(f"[PASS] {label:<18} {version}")
        except Exception as exc:  # Report all import failures without stopping early.
            packages_ok = False
            print(f"[FAIL] {label:<18} {type(exc).__name__}: {exc}")

    ollama = shutil.which("ollama")
    if not ollama and sys.platform == "darwin":
        candidate = "/Applications/Ollama.app/Contents/Resources/ollama"
        ollama = candidate if os.path.isfile(candidate) else None
    if not ollama and os.name == "nt":
        candidate = os.path.join(
            os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama.exe"
        )
        ollama = candidate if os.path.isfile(candidate) else None

    ollama_ok = bool(ollama)
    model_ok = False
    if ollama:
        try:
            result = subprocess.run(
                [ollama, "list"], capture_output=True, text=True, timeout=15, check=False
            )
            model_ok = result.returncode == 0 and "qwen2.5-coder:3b" in result.stdout
        except (OSError, subprocess.TimeoutExpired):
            model_ok = False
    print()
    print(f"[{pass_fail(ollama_ok)}] Ollama is installed")
    print(f"[{pass_fail(model_ok)}] Qwen2.5-Coder 3B is installed")
    packages_ok = packages_ok and ollama_ok and model_ok

    print()
    overall = env_ok and python_ok and packages_ok
    print("=" * 50)
    print(f"OVERALL: {pass_fail(overall)}")
    if not overall:
        print("Re-run the installer. If the failure remains, see README.md.")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
