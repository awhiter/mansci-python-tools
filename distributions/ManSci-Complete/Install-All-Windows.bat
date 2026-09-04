@echo off
setlocal
echo Management Science guided installer
echo Keep this window open and watch for prompts. Installation can take many minutes.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0payload\installer\bootstrap-windows.ps1" -PackageRoot "%~dp0." -Kind "Complete"
set "MANSCI_RESULT=%ERRORLEVEL%"
if not "%MANSCI_RESULT%"=="0" echo Installation did not complete. Read the message above and share the displayed log with staff.
echo This window will remain open until you press a key.
pause
exit /b %MANSCI_RESULT%
