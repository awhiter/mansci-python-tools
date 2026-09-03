@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"
echo ManSci Python Core Installer
echo ============================
set "CONDA_EXE="
for %%C in ("%USERPROFILE%\miniconda3\Scripts\conda.exe" "%LOCALAPPDATA%\miniconda3\Scripts\conda.exe" "%USERPROFILE%\anaconda3\Scripts\conda.exe") do if exist "%%~C" set "CONDA_EXE=%%~C"
if not defined CONDA_EXE for /f "delims=" %%C in ('where conda.exe 2^>nul') do if not defined CONDA_EXE set "CONDA_EXE=%%C"
if not defined CONDA_EXE goto no_conda
if not exist "%LOCALAPPDATA%\ManagementScience\Core" mkdir "%LOCALAPPDATA%\ManagementScience\Core"
>"%LOCALAPPDATA%\ManagementScience\Core\conda-path.txt" echo %CONDA_EXE%
"%CONDA_EXE%" env list | findstr /R /C:"^mansci-python " >nul
if errorlevel 1 ("%CONDA_EXE%" env create -f "%ROOT%payload\environment.yml") else ("%CONDA_EXE%" env update -n mansci-python -f "%ROOT%payload\environment.yml")
if errorlevel 1 goto failed
"%CONDA_EXE%" run --no-capture-output -n mansci-python python "%ROOT%payload\core_setup.py" initialise
if errorlevel 1 goto failed
where ollama.exe >nul 2>&1
if errorlevel 1 if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
where ollama.exe >nul 2>&1
if errorlevel 1 where winget.exe >nul 2>&1 && winget install --id Ollama.Ollama -e --accept-package-agreements --accept-source-agreements
where ollama.exe >nul 2>&1
if errorlevel 1 (echo WARNING: Install Ollama from https://ollama.com/download then rerun Core.) else (start "" /B ollama serve ^>nul 2^>^&1 & timeout /t 2 /nobreak ^>nul & ollama pull qwen2.5-coder:3b)
echo Core installation complete.
if not "%MANSCI_EMBEDDED%"=="1" pause
exit /b 0
:no_conda
echo ERROR: Miniconda was not found. Install it from https://docs.conda.io/projects/miniconda/en/latest/
if not "%MANSCI_EMBEDDED%"=="1" pause
exit /b 1
:failed
echo ERROR: Core installation failed.
if not "%MANSCI_EMBEDDED%"=="1" pause
exit /b 1
