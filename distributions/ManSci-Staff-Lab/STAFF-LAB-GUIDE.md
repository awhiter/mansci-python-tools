# ManSci Staff Lab — Azure OpenAI edition

This separate staff-only distribution adds Azure OpenAI GPT-4.1 to the same Management Science Python platform used by students. It contains **no Azure endpoint or key**. The first installation asks the staff user for the endpoint, deployment, API version and key, tests one small request, stores only non-secret settings in the staff support folder, and saves the key in macOS Login Keychain or Windows Credential Manager.

Azure usage may incur charges. Do not give students the resource key or publish it in notebooks, configuration, screenshots, logs, GitHub or teaching files. Revoke/rotate a key immediately if it may have been exposed.

## Install

Extract the entire ZIP locally, close ManSci tools, and run **Install-Windows.bat** or **Install-Mac.command**. The guided installer uses the current shared Core process: prerequisite checks, optional Miniconda/Ollama setup, explicit Conda terms, Python 3.13 environment update, Qwen download, standardised `Documents/ManSci Code`, offline ManSci Help, logs and permanent windowless launchers.

On Mac, an expected “Apple could not verify…” message means the installer is not Apple-notarised; it does not itself mean malware was detected. Only for the package from the trusted staff source, click Done, then use **System Settings → Privacy & Security → Open Anyway**. Never override an explicit malware/damage warning.

During installation, enter:

1. The Azure resource endpoint, normally `https://RESOURCE.openai.azure.com` (the launcher removes a pasted deployment suffix).
2. The exact deployment name, often `gpt-4.1` but not necessarily the model name.
3. The supported API version; the default is `2024-10-21`.
4. The Azure OpenAI key. Input is hidden.

Installation succeeds only after the Azure test passes and finishes with **INSTALLATION COMPLETE**. Existing healthy Core/model data and staff credentials are reused on reinstall. During an update, the installer stops the private background Staff Lab server so new personas and configuration take effect; save work and close the Staff Lab window first.

## Use

**ManSci Staff Lab** opens in a dedicated single application window. Reopening focuses the existing window and reconnects to its healthy authenticated Jupyter server; it does not intentionally start a duplicate. Closing the window leaves the server/kernels running for quick reconnection. Use **File → Shut Down** to stop the server and kernels.

The notebook home and sole Python kernel match the student tools:

- Working folder: `Documents/ManSci Code`, or the absolute path in `Documents/ManSci Code Home.txt`.
- Kernel: **Management Science Python** from `mansci-python`.

The previous staff package used `Documents/ManSci Staff Lab`. This installer does not delete or silently move that folder. Move any notebooks you still need into `Documents/ManSci Code` yourself so they appear with the rest of your programme work.

**ManSci Learning Assistant** starts with the configured Azure deployment, can use its notebook-aware tools, and mirrors the VM’s teaching approach: it explains reasoning, uses graduated help where appropriate, and prompts users to test and question AI output. The updated Staff Lab includes the VM-compatible Jupyter AI router and direct notebook, execution and JupyterLab tools. Its separate local MCP HTTP listener is disabled because those tools do not require it and its fixed port can conflict with another Jupyter process. **Qwen Local Chat** is a separate, tool-free local assistant: it accepts raw pasted Python, retains bounded recent chat context and produces code blocks, but does not reliably edit or understand the current notebook automatically. Never select the raw 3B model as a tool-using assistant. The ManSci assistant accepts an attachment without additional text and treats it as context, although adding a specific question will produce a more directed response.

Core also installs **ManSci Help** for the shared installation, platform, kernel, model and log FAQs.

## Staff support tools

The ZIP’s **Support Tools** folder contains platform-specific scripts to:

- Remove the saved Azure key. Rerun the installer afterwards to enter and test replacement details.
- Archive the Jupyternaut checkpoint database if chat reports a locked database or repeats indefinitely. Visible notebooks and `.chat` files are not deleted.

Close Staff Lab before using either tool. The scripts operate on the permanent installed support folder, so moving the extracted ZIP later does not break the main launcher.

## Troubleshooting and logs

- Mac installation logs: `~/Library/Logs/ManagementScience`.
- Windows installation logs: `%LOCALAPPDATA%\ManagementScience\Logs`.
- Staff Lab server logs: the `logs` folder beneath `~/Library/Application Support/ManSci Staff Lab` on Mac or `%APPDATA%\ManSci Staff Lab` on Windows.
- Azure failure: verify endpoint, exact deployment, API version, key/resource match, network access and Azure quota.
- Chat reports `NoneType` or `mcp_servers`: install release 2026.09.15.6 or later; this corrects the no-MCP compatibility path while retaining the direct Jupyter tools.
- Chat opens without a persona or has a disabled message box: close Staff Lab and rerun the current installer to completion. The installer stops the older background server; the next launch should select ManSci Learning Assistant.
- No kernel: close Staff Lab and rerun the current installer to completion.
- Qwen absent: verify Ollama is installed and the Qwen model stage passed; restart Staff Lab after installation.
- Slow Qwen: expected on modest hardware or VMs; Azure and local-model performance are independent.

When requesting support, provide OS/architecture, whether it is a VM, exact action/error, installer completion status and relevant logs. Remove tokens and confidential data. Never send the Azure key.


## What is deliberately VM-only

Linux user accounts, enrolment-specific folders, centrally managed teaching materials and **Copy to My Work** depend on the JupyterHub server and are not installed on staff computers. Staff Lab carries across the shared Python environment, supported Jupyter AI components and learning-assistant guidance that work safely on a local computer.
