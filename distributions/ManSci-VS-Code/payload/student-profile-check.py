"""Run this file in ManSci VS Code to check the active teaching environment."""

import importlib
import os
import platform
import sys


PACKAGES = (
    "numpy", "pandas", "scipy", "matplotlib", "sklearn", "sympy",
    "openpyxl", "networkx", "seaborn", "requests", "ipykernel",
)

print("Management Science Python check")
print("=" * 40)
print(f"Python executable: {sys.executable}")
print(f"Conda environment: {os.environ.get('CONDA_DEFAULT_ENV', '(not reported)')}")
print(f"Python version:    {platform.python_version()}")
print()

passed = "mansci-python" in sys.executable.lower()
print(f"[{'PASS' if passed else 'FAIL'}] mansci-python interpreter")
for package in PACKAGES:
    try:
        module = importlib.import_module(package)
        version = getattr(module, "__version__", "installed")
        print(f"[PASS] {package}: {version}")
    except Exception as exc:
        passed = False
        print(f"[FAIL] {package}: {exc}")

print("=" * 40)
print("OVERALL:", "PASS" if passed else "FAIL")
