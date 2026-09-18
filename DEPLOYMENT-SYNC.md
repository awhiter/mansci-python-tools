# ManSci deployment and asset synchronization record

Current coordinated release: **2026.09.18.2**
Shared Python Core: **2026.09.18.2**

Review this record before proposing or approving a change. Do not change a listed deployment or asset until Andrew has approved the cross-asset change set.

| Area | Canonical asset | Current relationship |
|---|---|---|
| JupyterHub VM Python, operating system and proxy | `mansci-python-server.yml`, `ubuntu-packages.txt`, `nginx-jupyterhub-upload.conf`, `jupyterhub-phone-preview.py`, `mansci-enrol/`, `mansci-learning-assistant/` and the deployed services | Same student/challenge Python modules as local Core; also includes server Jupyter AI and JupyterHub services. ManSci Learning Assistant package 1.0.4 and the shared `mansci_tools` runner are deployed. The documented module-lead archive workflow is supported by Ubuntu `unzip`. The HTTPS proxy permits request bodies up to 250 MB for teaching materials and ordinary course data. VM `run_app()` output includes an authenticated phone URL and credential-free QR code. |
| Student local tools | `distributions/ManSci-Core/payload/environment.yml` | Canonical cross-platform Python package set used by Core, Lab, Spyder, VS Code and Complete. |
| Staff Lab | `distributions/ManSci-Staff-Lab` | Embeds the current Core and adds Azure configuration, ManSci Learning Assistant and VM-compatible portable Jupyter AI components. |
| GitHub downloads | Six ZIPs plus `SHA256SUMS.txt` | Complete, Core, Lab, Spyder, Staff Lab and VS Code are rebuilt from the same installer source. |
| Student environment guidance | `ManSci_AI_Chat_Environment_Context.md` in the Scenario Week pack | Describes VM-first use, local JupyterLab, installed modules and learning guidance for external AI chats. |
| User/support guides | README, Distribution Guide, Staff Lab Guide, Staff Testing | Must state the current application release, Core version and platform-specific limits. |
| Scenario Week teaching assets | Launch deck, Challenge Brief, Coursework Brief, Facilitator Guide and artifact ZIP | Must use current environment names, supported packages, launch routes and AI-use guidance. |

## Capability boundaries

Shared across VM and local Core: the `mansci_tools` notebook/console runner, Python 3.13, Management Science Python kernel and the documented challenge modules including Streamlit, Flask, Dash, Gradio, Voilà and jupyter-server-proxy. Dash's optional source-built JupyterLab interface extension is centrally disabled because the supported application runner does not require it.

The runner displays phone access only when both JupyterHub's user-service prefix and the centrally configured HTTPS public base URL are present. Local installations remain bound to loopback and never display a phone QR code.

VM application logs use a private temporary directory per operating-system user. Do not restore the former shared `/tmp/mansci-app-logs` path.

Staff Lab and VM: ManSci Learning Assistant and the compatible Jupyter AI tool/router components. Staff Lab supplies Azure settings locally and keeps the key in the operating-system credential store.

Both personas require verification of ManSci-specific commands, capabilities and observed results. Unverified claims and illustrative output must be labelled. The VM additionally documents authorised `mansci-enrol MODULE --list` and `--count` operations for module leads.

VM only: JupyterHub accounts, enrolment-specific folders, centrally managed Teaching Materials and Copy to My Work.

The VM HTTPS server block must include `client_max_body_size 250m;`. Validate the complete Nginx configuration before reloading it. JupyterLab uploads use JSON/base64 encoding, so the maximum original file size is lower than the HTTP request-body limit.

Local only: desktop launchers, optional Spyder and VS Code, Ollama/Qwen local chat, and direct localhost application windows.

## Change review checklist

1. Identify affected deployment code, manifests and package lists.
2. Identify every guide, release note and teaching asset that describes the changed behaviour.
3. Present the complete proposed change set to Andrew and wait for approval.
4. Apply and test approved changes across each relevant deployment.
5. Rebuild editable documents, reading copies, teaching ZIPs and GitHub release assets.
6. Record versions, exclusions, test results and any required manual checks.
