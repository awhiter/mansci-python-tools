@echo off
setlocal
set /p "CONDA=" < "%LOCALAPPDATA%\ManagementScience\Core\conda-path.txt"
set "SCRIPT=%LOCALAPPDATA%\ManagementScience\Staff-Lab\staff_lab.py"
if not exist "%CONDA%" goto missing
if not exist "%SCRIPT%" goto missing
"%CONDA%" run --no-capture-output -n mansci-python python "%SCRIPT%" repair-chat-memory
pause
exit /b %ERRORLEVEL%
:missing
echo Staff Lab is not installed. Run its installer first.
pause
exit /b 1
