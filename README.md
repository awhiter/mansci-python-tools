# Management Science Python Tools

Cross-platform teaching distributions for a consistent Management Science Python environment across Spyder, JupyterLab and Visual Studio Code.

## Download

Staff testers should download **ManSci-Complete.zip** from the repository's [latest release](https://github.com/awhiter/mansci-python-tools/releases/latest). Separate Core, Spyder, JupyterLab, VS Code and staff-only Azure-enabled Staff Lab packages are also available there.

Do not download an installer from the source-code ZIP generated automatically by GitHub: use the named files attached under **Assets** on the release page.

## What the distributions provide

- A shared Conda environment named `mansci-python`, using Python 3.13.
- NumPy, pandas, SciPy, Statsmodels, Matplotlib, scikit-learn, SymPy, openpyxl, NetworkX, Seaborn and Requests.
- A GenAI challenge toolkit including Streamlit, Flask, Dash, Plotly, OpenAI, ipywidgets, Voilà, Gradio, PuLP, Altair, Pydantic, dotenv, Pillow, Beautiful Soup, Folium, geopy, Joblib, Faker, python-docx, ReportLab and qrcode.
- Authenticated VM classroom previews: `run_app()` displays an opaque QR code that any account on the same ManSci VM can open after signing in. The share contains no credential and expires with the app. Local installations remain loopback-only.
- VM Team Exchange: students can create or join a named cohort-wide team, then copy immutable, sender-labelled snapshots from anywhere in their workspace except `Teaching Materials` into a shared read-only folder. The current limit is six students; teaching staff have oversight access. Local installations are unchanged.
- One **Management Science Python** Jupyter kernel.
- One shared coding home: `Documents/ManSci Code`.
- Spyder with an isolated Light/Spyder configuration.
- JupyterLab with the managed kernel and a local Qwen coding assistant.
- A separate Staff Lab aligned with the student environment and the portable Jupyter AI/persona features used on the VM; Azure credentials are requested locally and kept out of the package.
- VS Code with an isolated teaching profile, Light+ theme, automatic interpreter/kernel configuration and local Continue assistant.
- Ollama and Qwen2.5-Coder 3B installation checks.
- Stable desktop launchers using the applications' standard icons.
- Windows Start menu launchers with matching icons, optionally pinnable by the user; no automatic taskbar changes.

The aim is to let students choose the most appropriate coding interface without changing environments or package versions. Python files, notebooks and data created in one tool remain available to the others.

## Prerequisites

The guided installer detects Conda and offers per-user [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install) installation if missing. Software and channel-term consent remain explicit; no manual acceptance commands are needed.

VS Code and Ollama are checked before Python packages. Windows Package Manager or existing Homebrew can install them with consent; otherwise the installer stops upfront with instructions. Choose local use if Ollama asks; its service starts automatically.

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

This is a **public staff-testing distribution**, not yet approved for students. Read [STAFF-TESTING.md](STAFF-TESTING.md). Automated checks have not certified fresh Windows/Mac installation. AI output must be reviewed and tested.

Maintainers: run `python tools/build_release.py` to synchronise embedded Core/helper copies and build six ZIPs/checksums under release-assets. Edit shared installer logic in installer/, not its generated copies.
