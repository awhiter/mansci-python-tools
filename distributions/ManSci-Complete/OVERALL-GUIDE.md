# Management Science tools — guided installation / staff testing

Release 2026.09.04.1 is public for staff testing, not yet approved for student rollout.

## Choose and start

ManSci Complete installs Core, Spyder, JupyterLab and VS Code. Individual tool packages embed the same versioned Core and update it if needed. All tools share Python 3.13 in `mansci-python`, the Management Science Python kernel and `Documents/ManSci Code`. The common scientific packages include Statsmodels.

Extract the ENTIRE ZIP to a local folder, not a network share or the Mac host's shared folder in a Windows VM. Close all ManSci tools before updating. Keep an internet connection and enough disk space for Python, applications and the roughly 2 GB Qwen model. Run Install-All-Windows.bat or Install-All-Mac.command for Complete; individual packages use Install-Windows.bat / Install-Mac.command.

## Five guided stages

Keep the window open. Watch for prompts in it AND other software installer windows. Quiet periods during package solving, installation and downloads may last many minutes, especially in a VM.

1. **Prerequisites.** VS Code (when selected) and Ollama are checked BEFORE Python packages. Windows offers Windows Package Manager installation when available; Mac offers Homebrew when already installed. Their installers may need your response. If automation is unavailable or declined, installation stops upfront with links. Install the missing application and rerun.
2. **Terms and Conda.** Existing Conda is discovered in common locations or a folder you specify. If missing, per-user Miniconda installation is offered after explicit consent. Channel terms are displayed before a separate acceptance question. Only after you agree are the acceptance commands run automatically. Staff must follow institutional licensing guidance; this installer does not determine eligibility.
3. **Python.** Core creates/updates the environment, checks imports, registers the kernel and prepares the shared folder. A healthy current Core is reused. No pruning or deletion of student work is performed.
4. **Local AI.** Ollama's local service starts automatically and is checked for readiness. You do NOT need to type `ollama` in a terminal. If Ollama opens, choose **local use**, not sign-in; no account is needed. Qwen2.5-Coder 3B is approximately 2 GB. `pulling` followed by letters/numbers and progress bars are normal. Existing models are reused. An AI failure is reported rather than labelled full success.
5. **Tools and launchers.** Selected settings/extensions and stable launchers are installed. Windows shortcut paths are constructed safely and checked after saving. Use the ManSci desktop launchers.

## Manual prerequisites when requested

- Miniconda: https://www.anaconda.com/docs/getting-started/miniconda/install — install for the operating system INSIDE a VM, not its host. Use the per-user defaults, then rerun. No manual channel-acceptance commands are required by this guided release.
- VS Code: https://code.visualstudio.com/download — use a Windows user installation; on Mac move the app into Applications.
- Ollama: https://ollama.com/download — install in its normal location and select local use if asked, then rerun.

You do not need to install a package manager just for ManSci. Homebrew itself is never installed automatically. Miniconda consent reference: https://www.anaconda.com/legal . On Mac, approve downloaded installers only through the normal OS security flow after checking their source; do not globally disable protections.

## Architecture

The Mac installer chooses Apple silicon or Intel Miniconda automatically. Windows 11 ARM VMware is identified explicitly: this release offers Windows x64 Miniconda under emulation with an extra confirmation. This is a staff-testing configuration, not a claim of native ARM package support. VS Code/Ollama use their vendor/package-manager builds. VM graphics acceleration and local-model performance need testing.

## Shared work and customisation

Core creates test.py, test.ipynb and a short README in Documents/ManSci Code without overwriting existing files. Keep code, notebooks and data there, in module/assignment subfolders. Back up important work. To change the home, edit Documents/ManSci Code Home.txt to contain one absolute folder path and restart the tools.

Spyder uses Light/Spyder and resets its initial Files/working directory to the shared home on launch. VS Code uses Light+, an isolated profile, Continue and a private ManSci kernelspec. JupyterLab uses the managed kernel and a tool-free local persona retaining recent chat context. Continue's first-run Hub card may need dismissing once, without sign-in. Small models still make mistakes and do not automatically know every file/cell.

## Errors and automatic logs

Top-level installers pause on BOTH success and failure. Read the error before closing. Logs are saved automatically:

- Windows: `%LOCALAPPDATA%\ManagementScience\Logs\install-<date-time>.log`. Paste `%LOCALAPPDATA%\ManagementScience\Logs` into File Explorer.
- Mac: `~/Library/Logs/ManagementScience/install-<date-time>.log`. Use Finder → Go → Go to Folder.

The precise path is printed at startup and on failure. Send the newest log to staff. Runtime logs, including ollama-service.log and launch.log, are in the per-user ManagementScience support folder's Logs directory. Fix the reported error and rerun; student work and existing model data are retained. Reopen Finder or sign out/in if standard desktop icons remain cached.

## Validation limits

Automated Python/configuration/package checks do not replace clean-machine tests. This release has NOT been end-to-end certified on fresh Windows x64, Windows ARM VMware, Intel Mac or Apple silicon Mac installations. See STAFF-TESTING.md in the repository before student rollout.
