# 2026.09.04.1 — Guided installation / staff testing

- Five announced stages, upfront VS Code/Ollama checks and persistent failure windows.
- Automatic per-user Miniconda offered after consent; existing/custom Conda supported.
- Channel terms displayed and accepted only after explicit agreement; no manual commands.
- Package-manager installation offers or clear manual prerequisite instructions.
- Ollama service started and awaited automatically; local-use/no-account guidance and explicit ~2 GB Qwen download message.
- Existing models reused; failed local AI is not reported as full success.
- Windows TargetPath corrected using Join-Path, safe arguments and shortcut read-back checks.
- Automatic logs, corrected batch variable handling, shared Core and preserved student work.
- Shared coding folder, light themes, Statsmodels, standard icons and local AI retained.

**For staff testing only.** Automated tests are not clean-machine certification. Windows ARM VMware uses x64 Python emulation and needs validation. See STAFF-TESTING.md.

Download ManSci-Complete.zip for all tools or individual packages. SHA256SUMS.txt covers the five ZIPs. This release supersedes 2026.09.03.2 for installation testing.
