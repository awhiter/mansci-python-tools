# 2026.09.21.6 — Shared local persona-stack compatibility / staff testing

Corrects Qwen Local Chat across both supported Persona Manager interfaces: version 0.1 uses `ychat`, while version 0.2 uses `chat`. The Qwen persona now selects the available interface safely in both Student Lab and Staff Lab, without changing its model, prompt, 12-message/12,000-character history limits or generation settings.

Student Lab and Staff Lab now pin the same Jupyter AI 3.2, Persona Manager 0.2, router, LiteLLM adapter and JupyterLab Chat versions. Because the two applications share the `mansci-python` environment, this prevents installing one Lab from silently downgrading the other's runtime. Staff-only Jupyternaut, tools and Azure functionality remain additive, while Student Lab continues to display only Qwen Local Chat.

# 2026.09.21.5 — Local Qwen persona correction / staff testing

Corrects Qwen Local Chat after the Persona Manager interface changed from `ychat` to `chat`. The repair leaves its Qwen2.5-Coder model, system guidance, 12-message/12,000-character history limits and generation settings unchanged.

Student ManSci Lab now loads personas exclusively from its own installed support folder and offers only **Qwen Local Chat**. It no longer displays the Staff Lab's ManSci Learning Assistant from the shared coding workspace or the Jupyternaut package entry point from the shared Python environment. Staff Lab and the JupyterHub VM retain their existing persona arrangements. Updating ManSci Lab stops its authenticated private server so the corrected registration is active on the next launch.

# 2026.09.21.4 — Restored UCL PowerPoint template / staff testing

Rebuilds both MSIN0023 Scenario Week PowerPoint decks as genuine descendants of the supplied UCL PowerPoint template. The editable files now retain the full UCL master, 42 layouts, theme, UCL Sans references and master logos while preserving the latest content and speaker notes.

The repository now includes the recovered source template and a mandatory validation tool. Future generated PowerPoints must use this source and pass structural template validation before packaging or publication. This release changes teaching assets only; VM and local software remain at the behaviour delivered in 2026.09.21.3.

# 2026.09.21.3 — Markdown preview workflow / staff testing

Markdown files now open in JupyterLab's built-in formatted **Markdown Preview** by default on the ManSci VM and in local ManSci Lab/Staff Lab. Students edit through **Open With → Editor** and may keep both views side by side. The setting is merged into the managed JupyterLab defaults without replacing unrelated settings.

The VM Learning Assistant, external-chat environment sheet, distribution guides and MSIN0023 Scenario Week materials now describe the same workflow, including the need to copy a view-only Team Exchange snapshot to My Work before editing. VM persona version 1.0.10 is included. Qwen Local Chat behaviour and prompting are unchanged.

# 2026.09.21.2 — Team Project Context guidance / staff testing

- Adds coordinated guidance for a shared `Team_Project_Context.md` across the VM Learning Assistant, external AI environment context and Scenario Week teaching assets.
- Guides teams to record scope, decisions, evidence, prototype files, tests, limitations and next actions, with one rotating context steward and dated Team Exchange snapshots.
- Makes clear that the context file is a working coordination record rather than independent evidence, and that teams must verify AI-proposed changes.
- Corrects the local ManSci Python version in the external context document to Python 3.13.
- Updates generated Scenario Week PowerPoint decks to current UCL Sans template branding.
- Leaves Qwen Local Chat unchanged.

# 2026.09.21.1 — Fixed VM persona model / staff testing

Removes the model-selection control from the VM's ManSci Learning Assistant. The persona now always uses the centrally configured model through its **Default** behavior, preventing students and staff from selecting catalogue entries that the managed VM does not support.

This is a VM-only interface correction. The local Staff Lab retains its useful Azure/local-model choice.

# 2026.09.20.2 — Notebook and chat provider separation / staff testing

Restores the collaboration content-provider token required by the Jupyter AI chat controls while leaving collaborative notebook/document providers disabled. This corrects the blank persona and model selectors introduced by the complete package shutdown in 2026.09.20.1.

Collaboration panels, shared links, global awareness, cursors and user-presence controls remain disabled and locked. Notebooks continue to use conventional loading, saving and cell execution, and the ManSci Learning Assistant is again available in chat.

# 2026.09.20.1 — Complete collaboration shutdown / staff testing

Disables and locks the complete Jupyter Collaboration interface and document-provider extensions on the VM. The previous correction disabled their notebook/text providers and the Jupyter AI live-document provider, but left the surrounding collaboration packages active. Those packages could continue waiting for a document provider, allowing a notebook to appear after a delay while preventing cell execution from reaching an otherwise healthy kernel.

The VM now uses JupyterLab's conventional document loading, saving and standard notebook executor throughout. Active module-lead and test-student servers are restarted so they cannot retain the previous front-end configuration. Team Exchange remains copy-based and unaffected.

# 2026.09.19.3 — Cohort-wide Team Exchange and conventional notebook saving / staff testing

Removes module and enrolment concepts from Team Exchange. Any ordinary ManSci student account can create one named team or join one by code, and the configured overall student limit remains six. Existing teams, memberships and shared files are retained. Team folders now appear directly beneath `Team Exchange/<team name>`, while teaching staff retain oversight access without occupying a student place.

**Copy to Team Exchange** is now available for ordinary files and folders anywhere in a student's visible workspace, including its top level and `My Work`; only centrally managed `Teaching Materials` is excluded. Shared snapshots remain read-only and Copy to My Work places an editable copy beneath `My Work/Team Exchange/<team name>`.

Disables and locks the remaining Jupyter AI live/server-document front-end extensions. These had continued to create document rooms and replace JupyterLab's normal save commands even after the standard collaborative providers were disabled. Notebooks now use conventional Jupyter saving throughout. The Learning Assistant retains its saved-workspace file reader but no longer depends on live collaborative document state.

# 2026.09.19.2 — VM Team Exchange / staff testing

Adds a VM-only, copy-based Team Exchange for short-lived student teams. An enrolled student can create a uniquely named team or join one with a short code; MSIN0023 currently permits six student members. Membership can change immediately without restarting a Jupyter server. Module leads and configured teaching staff can view all teams without occupying a student place.

Students share one file or folder from the module's `My Work` area using **Copy to Team Exchange**. Each contribution becomes a read-only, dated snapshot labelled with its sender, so previous contributions are retained. A team member uses **Copy to My Work** before editing or running a snapshot. The design does not enable simultaneous notebook editing or cross-home access. Team membership and sharing events are recorded in the protected VM service state.

The ManSci Learning Assistant, external-chat context, repository guidance and staff checks describe the same workflow. The VM extension also corrects JupyterLab's misleading `next yr.` display when a file timestamp differs from the browser clock by less than one minute. Local student and staff distributions remain unchanged because Team Exchange depends on JupyterHub accounts and VM storage.

# 2026.09.19.1 — Notebook recovery and conventional document saving / staff testing

Responds to a central MSIN0023 notebook being replaced by a stale browser state. The server log showed the module-lead browser reconnecting with “divergent history” at 09:22:41 UTC; one second later the collaborative provider replaced the current notebook with a single blank cell. This was automatic collaboration behaviour rather than an intentional user deletion or save.

The damaged file, uploaded original, central checkpoint and best recovery candidate are preserved in a restricted incident folder. The most recent available copy—32 cells from `student2`'s `My Work`—has been restored. No exact server-side copy of the later 22:57 version survived.

Notebook and text-file collaborative providers are now disabled and locked on the VM. These components arrived transitively with the beta Jupyternaut package used by the ManSci Learning Assistant; they were not required for a teaching collaboration workflow. JupyterLab returns to conventional file saving. Both collaboration packages' server-side cell executors are disabled and JupyterLab's standard executor is explicitly restored, so execution travels directly over the kernel channel without requiring a collaborative document room. Teaching Materials remain view-only for students, while module-lead accounts retain normal editing and execution access to the central source notebooks. The former 15-second collaboration-room setting has been removed. Before a central teaching file is replaced, Jupyter now stores a distinct prior version under `/srv/mansci/teaching-backups`, retaining up to 50 versions per file. Local ManSci distributions remain unchanged pending separate compatibility review of Staff Lab.

The Teaching Materials protection is now applied before JupyterLab begins kernel selection, removing the empty kernel prompt previously shown to students. **Copy to My Work** restores normal kernel preferences on the new notebook and waits for its configured kernel to be ready, so its cells can run immediately without a manual kernel restart.

# 2026.09.18.6 — Teaching Materials extension activation correction / staff testing

Corrects the deployment of the view-only Teaching Materials extension from 2026.09.18.5. The deployment had retained version 0.1.1 as a backup inside JupyterLab's live extension search directory. JupyterLab treated that backup as another installed copy, selected its old manifest and requested an obsolete JavaScript file that returned 404, so the view-only interface never appeared.

The legacy backup now resides outside JupyterLab's search path. JupyterLab reports version 0.2.0 as enabled and valid, and the `student2` server has been stopped so its next start loads the corrected manifest. The deployment script prevents a legacy backup from causing the same conflict in future. Local ManSci distributions remain unchanged.

# 2026.09.18.5 — View-only Teaching Materials notebooks / staff testing

Notebooks opened directly beneath `Teaching Materials` on the JupyterHub VM now display a clear view-only notice, disable editing and execution, prevent a kernel from starting, and provide a prominent **Copy to My Work** action. This stops a student from creating an apparently changed “ghost” notebook in JupyterLab's collaborative in-memory document after the protected source correctly rejects a save.

The underlying teaching file was never altered. JupyterLab's collaboration service retained the student's unsaved document separately from the kernel, so shutting down the kernel did not remove it. The VM now also releases an inactive collaboration document promptly. The affected `student2` server was restarted to clear its existing in-memory copy. Persona and external-chat guidance now describe the enforced workflow. Local ManSci distributions are unchanged because Teaching Materials and Copy to My Work are VM-only features.

# 2026.09.18.4 — Classroom sharing authorization and browser-session correction / staff testing

Fixes the 403 responses that prevented ordinary notebook servers from registering classroom shares and prevented other signed-in VM users from opening them. JupyterHub now grants the sharing service's narrow access scope to standard users and single-user server tokens while retaining their existing default scopes. The service also registers JupyterHub's OAuth callback route, correcting the subsequent 404 after a viewer successfully signed in. Existing active server tokens receive the same scope during deployment, so users do not need to restart their Jupyter servers.

After JupyterHub authenticates a viewer, the sharing service now uses one short-lived signed session for the app page and all of its assets. This prevents Streamlit's parallel JavaScript and stylesheet requests from each starting a separate OAuth exchange, which previously left the browser with a blank page.

# 2026.09.18.3 — VM classroom app sharing / staff testing

Adds a VM-only authenticated sharing route for applications launched with `run_app()`. The QR code now lets any holder of a valid account on the same ManSci VM sign in with their own credentials and interact with the presenter's running prototype. Shares use opaque temporary identifiers, validate that the loopback application port belongs to the presenting account, contain no credential, and expire when the application stops or becomes stale.

The displayed stopping instruction now imports `stop_app` explicitly, so it works even when the original notebook cell imported only `run_app`. Persona and student guidance use the same complete import pattern. Local ManSci distributions and their loopback-only behaviour are unchanged; no local installer release is required.

# 2026.09.18.2 — Preserve phone prototype route through sign-in / staff testing

Fixes the VM phone QR route introduced in 2026.09.18.1. A phone without an existing JupyterHub session could complete sign-in and then open the full JupyterLab interface because the application proxy destination was lost during authentication. The QR code now enters through JupyterHub's login handler and carries the exact per-user proxy path as its encoded post-login destination.

The normal notebook link remains unchanged for the already-authenticated desktop session. Phone access still requires the student's own VM sign-in, contains no password or access token, and lasts only while the student's server and app process are running.

# 2026.09.18.1 — Authenticated VM phone previews / staff testing

On the JupyterHub VM, `mansci_tools.run_app()` now displays a full authenticated HTTPS link and QR code for opening a student's prototype on their phone. The code contains no password or access token. The phone uses the student's normal ManSci VM sign-in, and the app remains available only while the VM server and application process run.

Local ManSci installations remain bound to loopback and do not display a phone QR code. Persona guidance, user documentation, external-chat context and Scenario Week teaching assets distinguish the VM workflow from local use and prohibit public tunnels, token-bearing links and external binding. Tests verify that phone URLs require both JupyterHub context and an HTTPS public base URL.

Application logs now use a private per-user temporary directory. This prevents the first VM account that launches an app from making the shared log folder unwritable for other students.

# 2026.09.17.2 — Verified persona guidance and enrolment reporting / staff testing

Adds authorised read-only `mansci-enrol MODULE --list` and `mansci-enrol MODULE --count` commands to the JupyterHub VM, with matching built-in help and module-lead guidance. This replaces the need to inspect the protected enrolment record directly.

The VM and Staff Lab ManSci Learning Assistant personas now explicitly prohibit invented commands, options, files, installed capabilities, counts, test outcomes and observed output. They must use explicit ManSci guidance or available inspection tools, label unverified claims, and distinguish hypothetical examples from real results. The student external-chat context carries the same accuracy rules. Shared Python Core remains 2026.09.17.1 because its package set is unchanged.

# 2026.09.17.1 — Suppress unnecessary Dash build prompt / staff testing

Disables Dash's optional `@plotly/dash-jupyterlab` interface extension at the managed-environment level and removes its source-build archive. Dash 4 installed this archive automatically, causing JupyterLab to recommend an interface build at login even though ManSci applications run through the supported `mansci_tools.run_app` and Jupyter proxy route.

Dash itself remains installed and available. The installer applies the setting without rebuilding JupyterLab, and the VM and local Core use the same configuration. Students should no longer be asked to build centrally managed JupyterLab application assets.

# 2026.09.16.3 — Flask proxy-port launch correction / staff testing

Fixes Flask links that returned a Jupyter proxy 500 response when a conventional student script used `app.run(debug=True)`. The runner now invokes the Flask CLI with its allocated loopback port and disables the debug reloader, so the source file does not need ManSci-specific port code.

The runner no longer displays a link when an application fails to listen on its assigned port. It terminates the failed process and raises an actionable error containing the log path and recent log output. Tests cover the managed Flask command and the no-link timeout behaviour.

# 2026.09.16.2 — Flask and Dash environment correction / staff testing

Adds Flask and Dash explicitly to the shared VM and local `mansci-python` environments. This corrects the mismatch in 2026.09.16.1, whose runner and persona advertised those application types while neither package was installed. Installer health checks, VM manifest, external-chat context, guides and tests now verify the same framework set.

The VM runner has been tested with small Flask and Dash applications using project-relative paths, automatic ports and the authenticated JupyterHub proxy route. Streamlit remains the recommended rapid interface, with Gradio and Voilà also available.

# 2026.09.16.1 — workspace-aware files and notebook application runner / staff testing

Adds the shared `mansci_tools` runner for ordinary Python scripts and browser applications. Students can run saved scripts and apps from a notebook or IPython console without learning Linux paths or terminal process management first. The runner resolves VM `~/notebooks` and local `Documents/ManSci Code` paths, starts in the project folder, allocates a port, supplies the authenticated Jupyter proxy link and provides stop/status controls.

The ManSci Learning Assistant can now find and read saved text and `.py` files within the visible workspace. Its guidance explains that open editor tabs must be saved, provides the Jupyter route first and adds the normal terminal command as supplementary learning, including the project-folder `cd` and Ctrl+C. VM, local distributions, guides and Scenario Week launch guidance are synchronized. The VM ManSci Learning Assistant package is now 1.0.2; the existing active server was not interrupted and will load the persona changes at its next normal start.

# 2026.09.15.7 — Jupyter AI chat-object compatibility correction / staff testing

Fixes the Jupyter AI beta failure `ManSciLearningAssistantPersona object has no attribute ychat`. Persona Manager 0.2 exposes the chat object as `chat`, while Jupyternaut 0.1.0b1 still reads its former `ychat` name once when constructing the conversation-memory thread ID. The ManSci persona now supplies a narrow compatibility alias to the same object.

This follows the 2026.09.15.6 no-MCP correction: ordinary and attachment-only turns can now proceed through attachment processing, direct-tool creation and conversation-memory setup. The VM persona has been audited for the same compatibility issue.

## Previous 2026.09.15.6 — Staff Lab prompt and attachment correction / staff testing


Fixes the Jupyter AI 3.2 failure `NoneType has no attribute mcp_servers` when the ManSci Learning Assistant processes a message while the optional local MCP server list is empty. The persona now retains its direct notebook, Python execution and JupyterLab tools without assuming an MCP server exists.

Attachment-only messages receive a short internal instruction to read the attachment as conversation context. Students and staff may still add a specific question when they want an immediate task performed.

The JupyterHub VM persona package was updated to 1.0.1 with the same compatibility alias. Its active student server was not interrupted and will load the correction at its next normal server start. The shared Python Core remains at 2026.09.15.2.

## Previous 2026.09.15.5 — Staff Lab persona startup correction / staff testing


Fixes a Staff Lab upgrade that could open a new chat without a usable persona. Staff Lab now selects ManSci Learning Assistant explicitly because Jupyter AI 3.2 retains an obsolete fallback persona ID. The installer also shuts down only the authenticated private Staff Lab server during an upgrade, ensuring newly installed personas and configuration load on the next launch.

The unnecessary standalone local MCP listener is disabled to avoid its fixed-port collision. Jupyternaut's direct notebook, execution and JupyterLab tools remain enabled. The shared Python Core and VM package set are unchanged.

Close the Staff Lab window, install this release, and wait for INSTALLATION COMPLETE. The installer stops the background Staff Lab server. On the next launch, create a chat and confirm ManSci Learning Assistant is selected and the message box is enabled.

## Previous 2026.09.15.4 — Synchronized deployments, guidance and Scenario Week assets / staff testing


Aligns the repository guides, Staff Lab acceptance checklist and Scenario Week teaching pack with the six current distributions and the JupyterHub VM. The release includes the student AI-chat environment context sheet and identifies which capabilities are shared, local-only or VM-only. A deployment synchronization record now defines the assets that must be reviewed together for future changes.

The shared Python Core remains at 2026.09.15.2 because its challenge package set is unchanged. Staff Lab retains the VM-compatible Jupyter AI components introduced in 2026.09.15.3. No VM software change is required for this release.

## Previous 2026.09.15.3 — Staff Lab alignment / staff testing

Adds the Azure-enabled Staff Lab as a sixth formal download. It uses the current student Core and adds the portable Jupyter AI 3.2 router, persona, tools, MCP and command-toolkit components used on the VM. The ManSci Learning Assistant mirrors the VM teaching approach. VM account management, centrally managed teaching folders and Copy to My Work remain server-only.

# 2026.09.15.2 — Ensure existing environments receive the GenAI toolkit / staff testing

Fixes the Complete and individual installers incorrectly reusing an older `mansci-python` environment after the GenAI toolkit was added. The internal Core version is now incremented, forcing an environment update on existing installations, and the runtime health check now imports every challenge package before reporting success.

Close all ManSci tools before installing this correction. Rerun the Complete installer; it will update the existing environment without deleting student work. After installation, start fresh Spyder and Jupyter kernels.

## Previous 2026.09.15.1 — GenAI challenge toolkit / staff testing

Adds the Python packages selected for the MSIN0023 GenAI team challenge to the shared `mansci-python` environment. Existing scientific and teaching packages remain in place. The added toolkit covers rapid apps and dashboards, notebook interaction, GenAI/API use, optimisation, maps, synthetic data, web parsing, structured validation and document/report generation. `jupyter-server-proxy` is included so JupyterLab can expose local Streamlit and similar services through the existing server.

The environment update is additive and uses pip dependency resolution inside the managed Conda environment. Reinstalling or updating an existing distribution preserves student work. This remains a staff-testing release; fresh Windows and Mac installation should be checked before student rollout.

## Previous 2026.09.04.13 — Retire legacy Check launchers / staff testing

The **ManSci Check** and **ManSci VS Code Check** desktop/application-menu launchers from older releases are now obsolete because **ManSci Help** provides the student-facing guidance. Installing this release removes only those exact legacy generated shortcuts/apps on Windows and Mac; it does not alter other desktop items or pins. The diagnostic Python scripts remain internal/available for staff-directed support, and the FAQ now names `student-profile-check.py` when its output is required.

The unused old Mac/Windows VS Code check-launch wrappers are no longer included in the payload. Release building now replaces embedded Core/tool trees instead of merging them, preventing deleted legacy files from persisting in later ZIPs. No environment, model or tool behaviour changes. Tests cover targeted cleanup, and archives are checked to ensure obsolete wrappers are absent.

## Previous 2026.09.04.12 — FAQ clarification / staff testing

Clarifies the Mac FAQ entry about an empty VS Code window after red-close. It now gives only the relevant recovery choices—use the pinned ManSci launcher or open `Documents/ManSci Code` through File → Open Folder—and no longer suggests reinstalling as part of ordinary use. Software behaviour is unchanged from 2026.09.04.11.

## Previous 2026.09.04.11 — Offline ManSci Help launcher / staff testing

Core now installs **ManSci Help** on the Desktop and in the Windows Start menu or Mac `~/Applications`. It opens a local, responsive HTML FAQ in the default browser and works offline. The heading displays the installed release for support. No Dock/taskbar item is added automatically.

The guide consolidates installation order and completion, macOS Gatekeeper approval, Windows prompts and pins, the shared code folder, tool-specific closing/quitting, Jupyter server reuse, Mac VS Code Dock limitations, interpreters/kernels, Spyder cells, local Qwen expectations, safe reinstalling, log locations and a support-information checklist. Security wording distinguishes an unnotarised warning from explicit malware detection and never recommends disabling general protections.

Every installer embeds Core, so rerunning any 2026.09.04.11 package installs or refreshes the same Help launcher even when the Python environment is already healthy. Tool/environment/model behaviour is unchanged from 2026.09.04.10. Automated tests cover launcher construction and archive content; staff should inspect links, readability and both platform launchers before student rollout.

## Previous 2026.09.04.10 — Reliable Mac launcher replacement / staff testing

The 2026.09.04.9 Complete installation did not reach VS Code on the reported Mac: it stopped signing the existing Lab desktop bundle, leaving VS Code at launcher 2026.09.04.8 and helper 0.2.0. Its Desktop folder is managed by Apple's File Provider and reapplied `com.apple.macl`/Finder metadata that recursive attribute cleanup could not reliably remove.

Mac launchers are now built and signed as fresh bundles in the permanent local support directory, then moved into Applications/Desktop only after signing succeeds. The existing generated launcher remains in place if building or signing fails; replacement uses a rollback and removes only its temporary backup after success. Student work is untouched. The VS Code Dock-reopen implementation itself is unchanged.

Quit all ManSci tools, install this Complete package, and require the final INSTALLATION COMPLETE message. Verify the installed ManSci VS Code bundle reports 2026.09.04.10 and its ManSci Startup extension reports 0.3.0, then repeat the red-close/Dock-icon test. No environment/model removal is needed.

## Previous 2026.09.04.9 — Mac VS Code Dock reopen fix / staff testing

Fixes the Mac behaviour where closing the ManSci VS Code window left the application active in the Dock—as is normal on macOS—but clicking that active icon opened an empty window. The isolated ManSci startup helper now detects that exact empty local-window case and reopens the current folder from `Documents/ManSci Code Home.txt` in the same window.

Safeguards prevent it replacing a deliberately opened folder/workspace, loose file, unsaved tab or remote window. It is enabled only in the ManSci-launched Mac process and does not affect ordinary VS Code or Windows. Command-Q remains the normal way to quit VS Code completely on Mac.

Install the updated VS Code ZIP (or Complete ZIP) with ManSci VS Code closed, then test: open from its launcher, close the window using red close, and click its still-active Dock icon. No environment/model removal is required. Nine automated helper tests pass; hands-on Dock verification remains required.

## Previous 2026.09.04.8 — Mac launcher update fix / staff testing

Fixes a Mac reinstall failure where Finder/download extended attributes on an existing generated `.app` launcher caused code signing to report “resource fork, Finder information, or similar detritus not allowed.” The installer now clears extended attributes only from each generated ManSci launcher immediately before signing; it does not touch student work or general application settings.

The reported installation stopped at Spyder before reaching Lab, leaving the old 3 September Lab launcher installed. Download and extract the updated Complete ZIP, close all ManSci tools, approve the Mac installer as documented, and rerun it. A successful run updates all three launchers; no environment or model removal is required. Automated tests check that cleanup occurs before signing, but the native Mac window still requires hands-on testing.

## Previous 2026.09.04.7 — First-run security guidance / documentation update

All package READMEs now explain the expected macOS “Apple could not verify…” message and give the file-specific Privacy & Security → Open Anyway steps. The distribution guide explains why an unverified installer warning differs from malware detection, the role and limits of established/open-source components, trusted download sources, missing approval options and when to stop and contact staff. It links to Apple's guidance and never asks users to disable general security protections.

Windows guidance clarifies that these Mac approval steps do not apply there, but Windows may show its own security or permission prompts; these are not guarantees of safety. All five ZIPs and the Complete package's overall guide have been refreshed. Software, environments and launcher behaviour are unchanged from 2026.09.04.6; working installations do not need reinstalling for this documentation-only release. Staff-testing status is retained.

## Previous 2026.09.04.6 — Spyder taskbar relaunch fix / staff testing

Spyder now receives an explicit ManSci taskbar identity, standard Spyder icon and relaunch command, matching its shortcut. Previously its running window retained Python's identity, so pinning that window could leave a non-working Python pin after closing. This uses the same window-property mechanism already used for Lab, without changing Spyder's windowless Python host or kernel handling. Lab and Code behaviour is unchanged.

Close Spyder, install the updated Spyder ZIP (or Complete ZIP), manually unpin the old Python/Spyder entry, and pin **ManSci Spyder** from Start. No environment/model removal is required. Test closing and reopening from the pin; Windows runtime verification remains a staff-machine check. Installer regression tests now check Spyder's matching shortcut/window identity and relaunch payload.

## Previous 2026.09.04.5 — Reusable Lab window and Code taskbar grouping

Lab now opens in its own native application-style window on Windows and Mac. Repeated launches request focus on that window rather than creating browser tabs. Closing the window preserves the notebook server; File → Shut Down stops it. The Windows installer checks WebView2, and installs the Python webview dependency automatically.

Windows ManSci Code windows now receive their launcher's taskbar identity, icon and relaunch command. Only the exact isolated ManSci user-data profile is matched; ordinary VS Code remains untouched. Spyder's console-window hotfix is retained. No pins are changed automatically.

Save work and close the tools, extract this release and rerun Complete (or Lab and VS Code individually). **Manually unpin the old Lab and Code entries, then pin their new ManSci Start menu entries.** No environment or model removal is needed.

Automated IPC ownership/authentication, server reuse, Python regression, VS Code helper and source compilation/profile-matching tests pass. Native Windows COM/taskbar behaviour still requires VM testing. The Mac renderer smoke test is skipped where no graphical desktop is available; this is not a claim of end-to-end native UI verification. Use STAFF-TESTING.md before student rollout.

## Previous 2026.09.04.4 — User-controlled Windows taskbar pins

All three tools now have dedicated windowless Windows launch executables with their standard icons, plus per-user Start menu entries. Users can pin/unpin these entries themselves. The installer never changes taskbar pins or policies. Pins retain the ManSci launch configuration and stable support-folder paths. Running VS Code/browser windows may appear separately: pin the ManSci Start menu entry, not their generic running-window buttons.

Close the tools, extract the new ZIP and rerun the Complete installer (or the individual tool installers). Find each ManSci entry in Start, right-click and choose Pin to taskbar / More → Pin to taskbar. No Core/model removal is needed. Windows compiles the small launcher locally using its existing .NET Framework compiler; a missing/blocked compiler produces an explicit installation error. Mac launcher behaviour is unchanged.

Automated tests include source compilation with a Windows Forms stub, not execution on Windows. Manual pin/unpin, icon and relaunch checks on Windows 11 are still required.

## Retained Spyder hotfix from 2026.09.04.3

Fixes a launcher regression from 2026.09.04.2: Spyder now retains its true pythonw.exe host identity. Jupyter Client uses this to set CREATE_NO_WINDOW for its kernel subprocesses; overriding it with python.exe prevented that safeguard. Spyder still selects python.exe from mansci-python for kernel execution. Lab and VS Code retain their separate executable handling.

A regression test covers Windows Spyder, Lab, VS Code and unchanged Mac identity. This has not yet been verified in a running Windows VM. Close Spyder normally, extract the new ZIP and rerun the Spyder or Complete installer. Do not repeatedly close the blank child consoles: that may interrupt a kernel and cause a restart.

## Retained changes from 2026.09.04.2

- Direct environment Python startup on Windows/Mac, without repeated Conda activation; activation paths captured once during installation.
- Windowless Windows launcher and Spyder process; Files pane explicitly shown after layout restoration.
- Lab opens the default browser via HTTP instead of a temporary HTML association. Authentication retained.
- Safe HTTP check to reuse an existing Lab server; removed the unsafe Windows process signal probe.
- Ollama startup no longer blocks Lab. Smaller 8K local-AI context, retained recent history and bounded replies; Lab requests 15-minute model retention.
- VS Code explicitly sets the interpreter through the Python extension API. Included ManSci Startup helper selects the live notebook controller, with readiness status, bounded retries and a visible fallback. Jupyter pinned to 2025.9.1 because this uses its exported unstable API.
- No recursive notebook rewrite/scan at startup. Stable icons, shared home, themes and teaching packages retained.
- Mac installer/launcher processes request a higher open-file limit to prevent VS Code watcher failures; no system-wide limit is changed.
- Guidance for Windows Security (Cancel inbound network permission for local-only use), VM performance and staff diagnostics. No firewall permissions granted automatically.

Close all ManSci apps, extract the new ZIP and rerun its installer. Current healthy Core and downloaded model are reused; launchers and tool configuration are updated.

**Staff testing only.** Automated Python/JavaScript tests, syntax checks and ZIP checks are not clean-machine Windows/Mac certification. In particular, confirm fresh-profile notebook selection, windowless Windows startup and firewall behaviour in the VM before student use. See STAFF-TESTING.md and DISTRIBUTION-GUIDE.md.

Download ManSci-Complete.zip for all tools, or individual packages. SHA256SUMS.txt covers the five distributions published by that historical release.
