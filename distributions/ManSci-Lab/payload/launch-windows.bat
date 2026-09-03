@echo off
set /p CONDA=<"%LOCALAPPDATA%\ManagementScience\Core\conda-path.txt"
"%CONDA%" run --no-capture-output -n mansci-python python "%LOCALAPPDATA%\ManagementScience\Lab\student_lab.py" launch
