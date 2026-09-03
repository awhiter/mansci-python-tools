@echo off
setlocal
set "ROOT=%~dp0"
echo Management Science Complete Installer
echo ======================================
set "MANSCI_EMBEDDED=1"
call "%ROOT%Packages\ManSci-Core\Install-Windows.bat" || exit /b 1
call "%ROOT%Packages\ManSci-Spyder\Install-Windows.bat" || exit /b 1
call "%ROOT%Packages\ManSci-Lab\Install-Windows.bat" || exit /b 1
call "%ROOT%Packages\ManSci-VS-Code\Install-Windows.bat" || exit /b 1
echo All Management Science tools are installed.
pause
