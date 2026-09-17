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
