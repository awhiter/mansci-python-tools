# Staff acceptance checklist

Record release, OS, architecture, VM/native, RAM/disk and log path for each test.

- [ ] Existing taskbar pins/order remain unchanged by installation.
- [ ] Each ManSci Start menu entry can be pinned/unpinned manually with its standard icon.
- [ ] Each pin relaunches the teaching setup after closing the tool, rebooting and moving the extracted ZIP folder.
- [ ] Manually replace old Lab/Code pins with new Start entries; Code groups under its ManSci pin after startup.
- [ ] Ordinary VS Code opened alongside ManSci Code keeps its own identity and profile.
- [ ] Repeated Lab launch focuses the existing native window without a second tab/window, including when minimised.
- [ ] Lab window close/reopen reuses the server; File → Shut Down stops it and subsequent relaunch restarts it.
- [ ] WebView2 missing/present checks and native window downloads, notebook editing, save, local chat and close confirmation work.

- [ ] Fresh Windows x64, Windows ARM VMware, Apple silicon Mac and Intel Mac.
- [ ] Missing VS Code/Ollama: install offer or manual guidance BEFORE Python packages.
- [ ] Missing Miniconda: consent, download, per-user installation and continuation.
- [ ] Existing Conda in default/custom locations reused, not overwritten.
- [ ] Declining consent stops without automatically accepting terms.
- [ ] Fresh channel terms accepted through the guided prompt; no manual commands.
- [ ] Offline/interrupted download leaves a visible error/log; rerun succeeds.
- [ ] Ollama local use needs no account; service starts without a terminal command.
- [ ] First model pull explains its size; rerun reuses it.
- [ ] Failed Core/AI/shortcut stages never report full success.
- [ ] Desktop launchers with paths containing spaces work, with no leftover terminal.
- [ ] test.py/test.ipynb run in mansci-python; Statsmodels imports in each tool.
- [ ] First notebook execution in VS Code needs no manual kernel selection.
- [ ] Wait for Preparing ManSci kernel to finish; confirm ManSci Startup output reports the installed environment.
- [ ] Cancel the VS Code inbound-network firewall prompt and verify local scripts/notebooks still run.
- [ ] Lab opens its dedicated window without asking for an HTML file association; a second launch reuses the window and server.
- [ ] Compare cold/warm startup and first/second AI replies; record CPU/GPU use with ollama ps and memory pressure.
- [ ] Spyder opens Files visibly and leaves no console while running or after closing.
- [ ] Spyder Files pane and all tools follow ManSci Code Home.txt.
- [ ] Light themes, standard icons and local chat/context work.
- [ ] Reinstall from another extracted folder preserves work, chats and launchers.

Do not approve student rollout until relevant platform results are recorded and failures resolved. Do not put credentials or sensitive student data in issue reports.
