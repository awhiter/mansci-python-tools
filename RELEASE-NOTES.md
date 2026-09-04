# 2026.09.04.7 — First-run security guidance / documentation update

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

Download ManSci-Complete.zip for all tools, or individual packages. SHA256SUMS.txt covers all five ZIPs.
