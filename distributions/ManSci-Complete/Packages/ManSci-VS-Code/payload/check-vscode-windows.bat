@echo off
setlocal
set "SUPPORT=%LOCALAPPDATA%\ManagementScienceVSCode"
set "CONDA_EXE="
for %%C in ("%USERPROFILE%\miniconda3\Scripts\conda.exe" "%LOCALAPPDATA%\miniconda3\Scripts\conda.exe" "%USERPROFILE%\anaconda3\Scripts\conda.exe" "%LOCALAPPDATA%\anaconda3\Scripts\conda.exe") do if not defined CONDA_EXE if exist "%%~C" set "CONDA_EXE=%%~C"
if not defined CONDA_EXE for /f "delims=" %%C in ('where conda.exe 2^>nul') do if not defined CONDA_EXE set "CONDA_EXE=%%C"
set "CODE_EXE="
for %%C in ("%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd" "%ProgramFiles%\Microsoft VS Code\bin\code.cmd" "%ProgramFiles(x86)%\Microsoft VS Code\bin\code.cmd") do if not defined CODE_EXE if exist "%%~C" set "CODE_EXE=%%~C"
if not defined CODE_EXE for /f "delims=" %%C in ('where code.cmd 2^>nul') do if not defined CODE_EXE set "CODE_EXE=%%C"
if not defined CONDA_EXE (
  echo ERROR: Miniconda was not found.
  goto :end
)
if not defined CODE_EXE (
  echo ERROR: Visual Studio Code was not found.
  goto :end
)
set "MANSCI_VSCODE_SUPPORT=%SUPPORT%"
"%CONDA_EXE%" run --no-capture-output -n mansci-python python "%SUPPORT%\launcher\vscode_setup.py" status --conda "%CONDA_EXE%" --code "%CODE_EXE%" --source "%SUPPORT%\launcher"
:end
echo.
pause
