# Staff acceptance checklist

Record release, OS, architecture, VM/native, RAM/disk and log path for each test.

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
- [ ] Lab opens the default browser without asking for an HTML file association; a second launch reuses the server.
- [ ] Compare cold/warm startup and first/second AI replies; record CPU/GPU use with ollama ps and memory pressure.
- [ ] Spyder opens Files visibly and leaves no console while running or after closing.
- [ ] Spyder Files pane and all tools follow ManSci Code Home.txt.
- [ ] Light themes, standard icons and local chat/context work.
- [ ] Reinstall from another extracted folder preserves work, chats and launchers.

Do not approve student rollout until relevant platform results are recorded and failures resolved. Do not put credentials or sensitive student data in issue reports.
