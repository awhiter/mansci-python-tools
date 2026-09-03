@echo off
set /p CONDA=<"%LOCALAPPDATA%\ManagementScience\Core\conda-path.txt"
set "WORK=%USERPROFILE%\Documents\ManSci Code"
if exist "%USERPROFILE%\Documents\ManSci Code Home.txt" set /p WORK=<"%USERPROFILE%\Documents\ManSci Code Home.txt"
set "SPYDER_CONFDIR=%LOCALAPPDATA%\ManagementScience\Spyder"
cd /d "%WORK%"
"%CONDA%" run --no-capture-output -n mansci-python spyder --new-instance
