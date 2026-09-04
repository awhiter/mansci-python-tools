# 2026.09.04.3 — Spyder Windows child-console hotfix / staff testing

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
