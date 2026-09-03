# Management Science Python Tools

Cross-platform teaching distributions for a consistent Management Science Python environment across Spyder, JupyterLab and Visual Studio Code.

## Download

Most students should download **ManSci-Complete.zip** from the repository's [latest release](../../releases/latest). Separate Core, Spyder, JupyterLab and VS Code packages are also available there.

Do not download an installer from the source-code ZIP generated automatically by GitHub: use the named files attached under **Assets** on the release page.

## What the distributions provide

- A shared Conda environment named `mansci-python`, using Python 3.13.
- NumPy, pandas, SciPy, Statsmodels, Matplotlib, scikit-learn, SymPy, openpyxl, NetworkX, Seaborn and Requests.
- One **Management Science Python** Jupyter kernel.
- One shared coding home: `Documents/ManSci Code`.
- Spyder with an isolated Light/Spyder configuration.
- JupyterLab with the managed kernel and a local Qwen coding assistant.
- VS Code with an isolated teaching profile, Light+ theme, automatic interpreter/kernel configuration and local Continue assistant.
- Ollama and Qwen2.5-Coder 3B installation checks.
- Stable desktop launchers using the applications' standard icons.

The aim is to let students choose the most appropriate coding interface without changing environments or package versions. Python files, notebooks and data created in one tool remain available to the others.

## Prerequisites

Install [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/) before using any distribution. Full Anaconda is not required.

Students using the VS Code package must also install ordinary [Visual Studio Code](https://code.visualstudio.com/) first. The installers check Ollama and attempt to install it where supported; otherwise they direct the student to [ollama.com/download](https://ollama.com/download).

The single macOS installer detects Apple silicon and Intel automatically.

## Installation

1. Download and extract `ManSci-Complete.zip` from the latest release.
2. On macOS, run `Install-All-Mac.command`.
3. On Windows, run `Install-All-Windows.bat`.
4. Start the tools using the new **ManSci Spyder**, **ManSci Lab** or **ManSci VS Code** desktop launcher.

Each individual tool installer embeds and checks the required Core version. Reinstallation updates the setup without deleting student code.

See [DISTRIBUTION-GUIDE.md](DISTRIBUTION-GUIDE.md) for package choices, architecture details, shared-folder behaviour and troubleshooting context.

## Repository contents

Editable installer sources are under [`distributions`](distributions). Ready-to-use ZIP files are published as formal GitHub Release assets rather than committed to Git history.

## Release integrity

SHA-256 checksums are provided in [`SHA256SUMS.txt`](SHA256SUMS.txt) and attached to each release.

## Support status

This is a private teaching distribution currently prepared for testing. Generated AI output should always be reviewed and run before use.
