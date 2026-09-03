@echo off
setlocal
set "ROOT=%~dp0"
set "MARKER=%LOCALAPPDATA%\ManagementScience\Core\version.txt"
set "CURRENT="
if exist "%MARKER%" set /p CURRENT=<"%MARKER%"
if not "%CURRENT%"=="2026.09.03.1" (set "MANSCI_EMBEDDED=1" & call "%ROOT%payload\core\Install-Windows.bat" || exit /b 1)
set /p CONDA=<"%LOCALAPPDATA%\ManagementScience\Core\conda-path.txt"
set "SUPPORT=%LOCALAPPDATA%\ManagementScience\Spyder"
if not exist "%SUPPORT%" mkdir "%SUPPORT%"
copy /Y "%ROOT%payload\launch-windows.bat" "%SUPPORT%\launch.bat" >nul
copy /Y "%ROOT%payload\hidden.vbs" "%SUPPORT%\hidden.vbs" >nul
copy /Y "%ROOT%payload\icons\spyder.ico" "%SUPPORT%\spyder.ico" >nul
"%CONDA%" run --no-capture-output -n mansci-python python "%ROOT%payload\spyder_setup.py" || exit /b 1
powershell -NoProfile -ExecutionPolicy Bypass -Command "$w=New-Object -ComObject WScript.Shell;$d=[Environment]::GetFolderPath('Desktop');$p=Join-Path $d 'ManSci Spyder.lnk';Remove-Item $p -Force -ErrorAction SilentlyContinue;$s=$w.CreateShortcut($p);$s.TargetPath='$env:WINDIR\System32\wscript.exe';$s.Arguments='""%SUPPORT%\hidden.vbs" "%SUPPORT%\launch.bat""';$s.IconLocation='%SUPPORT%\spyder.ico,0';$s.Save()"
echo ManSci Spyder installed.
if not "%MANSCI_EMBEDDED%"=="1" pause
