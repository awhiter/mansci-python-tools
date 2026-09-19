# Staff acceptance checklist

Record release, OS, architecture, VM/native, RAM/disk and log path for each test.

- [ ] Existing taskbar pins/order remain unchanged by installation.
- [ ] ManSci Help appears on Desktop and in Start / `~/Applications`, opens the local FAQ in the default browser, shows the installed release and works offline.
- [ ] Upgrade removes only old ManSci Check / ManSci VS Code Check launchers from Desktop and application menu; no unrelated shortcut, Dock item or taskbar pin changes.
- [ ] Help remains usable at narrow and enlarged text sizes; internal navigation and external links work; security wording matches the current platform behaviour.
- [ ] Each ManSci Start menu entry can be pinned/unpinned manually with its standard icon.
- [ ] Each pin relaunches the teaching setup after closing the tool, rebooting and moving the extracted ZIP folder.
- [ ] Replace the old Spyder/Python pin; pin the running Spyder window as well as testing the Start entry. After closing, it retains the Spyder icon/name and relaunches successfully without blank consoles.
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
- [ ] Mac: close ManSci VS Code's window with red close, click its active Dock icon and confirm the shared folder reopens in the same window; Command-Q quits it.
- [ ] Mac: an explicit workspace, loose file, unsaved tab and remote window are not replaced by the Dock reopen helper; ordinary VS Code is unaffected.
- [ ] Wait for Preparing ManSci kernel to finish; confirm ManSci Startup output reports the installed environment.
- [ ] Cancel the VS Code inbound-network firewall prompt and verify local scripts/notebooks still run.
- [ ] Lab opens its dedicated window without asking for an HTML file association; a second launch reuses the window and server.
- [ ] Compare cold/warm startup and first/second AI replies; record CPU/GPU use with ollama ps and memory pressure.
- [ ] Spyder opens Files visibly and leaves no console while running or after closing.
- [ ] Spyder Files pane and all tools follow ManSci Code Home.txt.
- [ ] Light themes, standard icons and local chat/context work.
- [ ] Reinstall from another extracted folder preserves work, chats and launchers.


## Staff Lab and deployment alignment

- [ ] Install ManSci Staff Lab from the current release on a clean profile and as an upgrade from the previous Staff Lab.
- [ ] Confirm it uses the Management Science Python kernel and Documents/ManSci Code without changing student work.
- [ ] Confirm the Azure endpoint/deployment test succeeds and the key is stored only in macOS Keychain or Windows Credential Manager.
- [ ] Confirm a new chat selects ManSci Learning Assistant automatically, shows its identity and enables the message box.
- [ ] Upgrade while an older private Staff Lab server remains in the background; confirm the installer stops it and the next launch loads the new personas.
- [ ] Confirm ManSci Learning Assistant follows the same learning, verification and secret-handling guidance as the VM persona.
- [ ] Confirm Jupyter AI notebook, execution and JupyterLab tools and the router load without repeated-message or locked-database failures.
- [ ] Confirm the standalone local MCP listener is disabled and no port-3001 collision appears in a fresh server log.
- [ ] Send an ordinary prompt with no MCP server configured; confirm the direct notebook, Python execution and JupyterLab tools load without a `NoneType`/`mcp_servers` error.
- [ ] Send an attachment with no added text; confirm it is accepted as conversation context and does not fail before model invocation.
- [ ] Confirm an ordinary and attachment-only turn both proceed through conversation-memory setup without a missing `ychat` attribute.
- [ ] Confirm Qwen Local Chat remains available without Azure and is not configured as a tool-using assistant.
- [ ] Confirm reset-key and repair-chat support tools operate on the installed support folder.
- [ ] Compare the VM manifest, student environment.yml, Staff Lab requirements, user guides and Scenario Week environment sheet against DEPLOYMENT-SYNC.md.
- [ ] On the VM, confirm notebook and text-file RTC providers are disabled and locked; restart a user server with an open browser tab and confirm stale content cannot overwrite the server file.
- [ ] As a module lead, run a code cell in the restored central teaching notebook and confirm the standard JupyterLab executor starts the Management Science Python kernel normally.
- [ ] As a module lead, edit and save a central teaching notebook; confirm the previous version appears beneath `/srv/mansci/teaching-backups/<module>/versions` and the saved notebook reopens correctly.
- [ ] As a student, confirm a Teaching Materials notebook remains view-only and **Copy to My Work** opens an editable conventional notebook in `My Work`.
- [ ] On the VM, create a named Team Exchange as one student, join it by code as another, share a top-level notebook and a folder from `My Work`, and confirm both appear as dated sender-labelled snapshots without overwriting earlier versions. Confirm `Teaching Materials` cannot be shared.
- [ ] Confirm Team Exchange snapshots are read-only, **Copy to My Work** creates an editable copy, leaving removes access immediately, the configured student limit is enforced, and authorised teaching staff can view all teams without counting towards that limit.
- [ ] Create, edit, save, close and reopen notebooks at the workspace top level and in `My Work`; confirm conventional saves retain cells and outputs and that no `ServerDocsApp` room handles the files.
- [ ] Confirm the ManSci Learning Assistant can still locate a saved notebook or `.py` file and provide guidance after RTC document providers are disabled.

Do not approve student rollout until relevant platform results are recorded and failures resolved. Do not put credentials or sensitive student data in issue reports.

- [ ] Open and save a `.py` file, refer to it by filename in chat, and confirm the assistant locates and reads it without asking for `~/notebooks`.
- [ ] Run an ordinary script with `%run` and a Streamlit file with `mansci_tools.run_app`; confirm relative project files work and the proxied app link opens.
- [ ] Confirm the assistant presents a terminal equivalent second, explains `cd` and Ctrl+C, and does not require terminal use.

- [ ] Launch a conventional Flask file ending in `app.run(debug=True)` through `run_app(..., kind="flask")`; confirm the allocated proxy link opens and no default-port debug reloader remains.
- [ ] Launch a process that never opens `MANSCI_APP_PORT`; confirm the runner terminates it, raises an actionable error and displays no app link.
