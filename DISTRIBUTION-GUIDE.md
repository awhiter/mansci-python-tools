# Management Science Python Teaching Distributions

## Purpose

These distributions give Management Science students a consistent Python platform across the programme. **Spyder**, **JupyterLab** and **VS Code** all:

- run the same `mansci-python` Conda environment;
- use the same scientific, data-analysis and optimisation-supporting Python packages;
- open the same `Documents/ManSci Code` home folder;
- use the **Management Science Python** notebook kernel; and
- use the same local Qwen2.5-Coder 3B model where an AI interface is provided.

Code and data are therefore portable between tools. A `.py` file developed with Spyder can be opened in VS Code; a notebook developed in ManSci Lab can be opened in VS Code; both see the same package versions and files.

The common environment includes NumPy, pandas, SciPy, Statsmodels, Matplotlib, scikit-learn, SymPy, openpyxl, NetworkX, Seaborn and Requests, alongside the packages required by the three applications.

## Which download to use

- **ManSci Core** installs the shared environment, kernel, coding home, tests, Ollama and Qwen model. Use this alone only when preparing the foundation.
- **ManSci Spyder** adds the beginner-friendly scientific IDE, isolated settings and launcher.
- **ManSci Lab** adds JupyterLab, the local conversational coding assistant and launcher.
- **ManSci VS Code** adds the isolated teaching profile, Python/Jupyter extensions, Continue local assistant and launcher. Ordinary VS Code must first be installed from [code.visualstudio.com](https://code.visualstudio.com/).
- **ManSci Complete** contains all four packages and a master installer. This is the simplest choice for students expected to use all three tools.

Each tool installer contains the required Core version. If Core is absent or out of date, the tool installer updates it first. Reinstallation updates components safely and does not overwrite student work.

## Recommended order

For the Complete package:

1. Install Miniconda from the [official Miniconda page](https://docs.conda.io/projects/miniconda/en/latest/).
2. Install ordinary VS Code from [code.visualstudio.com](https://code.visualstudio.com/).
3. Extract the entire ZIP.
4. Run `Install-All-Mac.command` or `Install-All-Windows.bat`.

For separate packages, install Core first and then any tool packages. It is also safe to start directly with a tool package because it checks Core automatically.

## Apple silicon and Intel Macs

One Mac installer supports both architectures. It detects `arm64` (Apple silicon) or `x86_64` (Intel), and Conda obtains packages for that architecture. Students must choose the matching Miniconda installer; no separate ManSci ZIP is necessary.

## Shared coding home

All launchers open:

- Windows: `Documents\ManSci Code`
- macOS: `Documents/ManSci Code`

Core creates a README plus `test.py` and `test.ipynb` there. Students should keep Python code, notebooks and associated data in this folder, organised into subfolders as needed. To change the home, edit `Documents/ManSci Code Home.txt`, enter one full folder path, then restart the ManSci tools.

## Ollama and local AI

Core checks for Ollama and downloads `qwen2.5-coder:3b`. On Windows it attempts installation through `winget`; on macOS it attempts installation through Homebrew when available. If automatic installation is unavailable, it directs the student to [ollama.com/download](https://ollama.com/download); rerunning Core completes the model setup afterward.

Qwen runs locally and needs no shared API key. It is deliberately a small teaching model, so generated code must be reviewed and tested. ManSci Lab provides the local Jupyter chat experience, while ManSci VS Code provides Continue chat, inline edits and completions. Spyder remains a focused coding environment without an additional AI panel.

Desktop launchers use the standard Spyder, JupyterLab and Visual Studio Code icons, while retaining their short ManSci names so students can distinguish the managed teaching setup from an ordinary installation.

## Reinstallation and files

Launchers are copied to stable per-user support folders and never point into an extracted ZIP. A distribution can therefore be moved or deleted after installation. Rerunning an installer refreshes its launcher and configuration without deleting `ManSci Code`, conversations or unrelated environment packages.
