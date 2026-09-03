@echo off
setlocal
set "SUPPORT=%LOCALAPPDATA%\ManagementScienceVSCode"
set "CONDA_EXE="
for %%C in ("%USERPROFILE%\miniconda3\Scripts\conda.exe" "%LOCALAPPDATA%\miniconda3\Scripts\conda.exe" "%USERPROFILE%\anaconda3\Scripts\conda.exe" "%LOCALAPPDATA%\anaconda3\Scripts\conda.exe") do if not defined CONDA_EXE if exist "%%~C" set "CONDA_EXE=%%~C"
if not defined CONDA_EXE for /f "delims=" %%C in ('where conda.exe 2^>nul') do if not defined CONDA_EXE set "CONDA_EXE=%%C"

set "CODE_EXE="
for %%C in ("%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd" "%ProgramFiles%\Microsoft VS Code\bin\code.cmd" "%ProgramFiles(x86)%\Microsoft VS Code\bin\code.cmd") do if not defined CODE_EXE if exist "%%~C" set "CODE_EXE=%%~C"
if not defined CODE_EXE for /f "delims=" %%C in ('where code.cmd 2^>nul') do if not defined CODE_EXE set "CODE_EXE=%%C"

if not defined CONDA_EXE exit /b 10
if not defined CODE_EXE exit /b 11
set "OLLAMA_EXE="
for %%O in ("%LOCALAPPDATA%\Programs\Ollama\ollama.exe" "%ProgramFiles%\Ollama\ollama.exe") do if not defined OLLAMA_EXE if exist "%%~O" set "OLLAMA_EXE=%%~O"
if not defined OLLAMA_EXE for /f "delims=" %%O in ('where ollama.exe 2^>nul') do if not defined OLLAMA_EXE set "OLLAMA_EXE=%%O"
if defined OLLAMA_EXE (
  "%OLLAMA_EXE%" list >nul 2>&1
  if errorlevel 1 start "" /B "%OLLAMA_EXE%" serve >"%TEMP%\mansci-ollama.log" 2>&1
)
set "MANSCI_VSCODE_SUPPORT=%SUPPORT%"
"%CONDA_EXE%" run --no-capture-output -n mansci-python python "%SUPPORT%\launcher\vscode_setup.py" launch --conda "%CONDA_EXE%" --code "%CODE_EXE%" --source "%SUPPORT%\launcher"
exit /b %errorlevel%
