@echo off
setlocal
set "ROOT=%~dp0"
set "MARKER=%LOCALAPPDATA%\ManagementScience\Core\version.txt" & set "CURRENT="
if exist "%MARKER%" set /p CURRENT=<"%MARKER%"
if not "%CURRENT%"=="2026.09.03.1" (set "MANSCI_EMBEDDED=1" & call "%ROOT%payload\core\Install-Windows.bat" || exit /b 1)
set /p CONDA=<"%LOCALAPPDATA%\ManagementScience\Core\conda-path.txt"
"%CONDA%" run --no-capture-output -n mansci-python python -m pip install --upgrade --upgrade-strategy only-if-needed -r "%ROOT%payload\requirements-student.txt" || exit /b 1
set "SUPPORT=%LOCALAPPDATA%\ManagementScience\Lab" & if not exist "%SUPPORT%" mkdir "%SUPPORT%"
xcopy /E /I /Y "%ROOT%payload\personas" "%SUPPORT%\personas" >nul & xcopy /E /I /Y "%ROOT%payload\jupyter-config" "%SUPPORT%\jupyter-config" >nul
copy /Y "%ROOT%payload\student_lab.py" "%SUPPORT%\student_lab.py" >nul & copy /Y "%ROOT%payload\launch-windows.bat" "%SUPPORT%\launch.bat" >nul & copy /Y "%ROOT%payload\hidden.vbs" "%SUPPORT%\hidden.vbs" >nul & copy /Y "%ROOT%payload\icons\jupyterlab.ico" "%SUPPORT%\jupyterlab.ico" >nul
powershell -NoProfile -ExecutionPolicy Bypass -Command "$w=New-Object -ComObject WScript.Shell;$d=[Environment]::GetFolderPath('Desktop');$p=Join-Path $d 'ManSci Lab.lnk';Remove-Item $p -Force -ErrorAction SilentlyContinue;$s=$w.CreateShortcut($p);$s.TargetPath='$env:WINDIR\System32\wscript.exe';$s.Arguments='""%SUPPORT%\hidden.vbs" "%SUPPORT%\launch.bat""';$s.IconLocation='%SUPPORT%\jupyterlab.ico,0';$s.Save()"
echo ManSci Lab installed.
if not "%MANSCI_EMBEDDED%"=="1" pause
