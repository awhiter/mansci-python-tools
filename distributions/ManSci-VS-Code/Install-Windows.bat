@echo off
setlocal
set "ROOT=%~dp0" & set "MARKER=%LOCALAPPDATA%\ManagementScience\Core\version.txt" & set "CURRENT="
if exist "%MARKER%" set /p CURRENT=<"%MARKER%"
if not "%CURRENT%"=="2026.09.03.1" (set "MANSCI_EMBEDDED=1" & call "%ROOT%payload\core\Install-Windows.bat" || exit /b 1)
set /p CONDA_EXE=<"%LOCALAPPDATA%\ManagementScience\Core\conda-path.txt"
set "CODE_EXE="
for %%C in ("%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd" "%ProgramFiles%\Microsoft VS Code\bin\code.cmd") do if not defined CODE_EXE if exist "%%~C" set "CODE_EXE=%%~C"
if not defined CODE_EXE (echo ERROR: Install Visual Studio Code from https://code.visualstudio.com/ then rerun this installer. & start https://code.visualstudio.com/ & pause & exit /b 1)
set "SUPPORT=%LOCALAPPDATA%\ManagementScienceVSCode" & set "LAUNCHER=%SUPPORT%\launcher"
if not exist "%LAUNCHER%" mkdir "%LAUNCHER%"
for %%F in (vscode_setup.py launch-vscode-windows.bat check-vscode-windows.bat windows-hidden-launch.vbs create-windows-shortcuts.ps1 STUDENT-GUIDE.md student-profile-check.py) do copy /Y "%ROOT%payload\%%F" "%LAUNCHER%\%%F" >nul
if not exist "%SUPPORT%\icons" mkdir "%SUPPORT%\icons"
copy /Y "%ROOT%payload\icons\vscode.ico" "%SUPPORT%\icons\vscode.ico" >nul
set "MANSCI_VSCODE_SUPPORT=%SUPPORT%"
"%CONDA_EXE%" run --no-capture-output -n mansci-python python "%LAUNCHER%\vscode_setup.py" configure --conda "%CONDA_EXE%" --code "%CODE_EXE%" --source "%LAUNCHER%" || exit /b 1
"%CONDA_EXE%" run --no-capture-output -n mansci-python python "%LAUNCHER%\vscode_setup.py" install-extensions --conda "%CONDA_EXE%" --code "%CODE_EXE%" --source "%LAUNCHER%" || exit /b 1
powershell -NoProfile -ExecutionPolicy Bypass -File "%LAUNCHER%\create-windows-shortcuts.ps1" -LauncherDirectory "%LAUNCHER%" -SupportDirectory "%SUPPORT%"
echo ManSci VS Code installed with the Light+ theme.
if not "%MANSCI_EMBEDDED%"=="1" pause
