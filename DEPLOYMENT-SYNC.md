# ManSci deployment and asset synchronization record

Current coordinated release: **2026.09.21.6 (shared local persona-stack compatibility / staff testing)**
Shared Python Core: **2026.09.21.3**

Review this record before proposing or approving a change. Do not change a listed deployment or asset until Andrew has approved the cross-asset change set.

| Area | Canonical asset | Current relationship |
|---|---|---|
| JupyterHub VM Python, operating system and proxy | `mansci-python-server.yml`, `ubuntu-packages.txt`, `nginx-jupyterhub-upload.conf`, `jupyterhub-phone-preview.py`, `mansci-app-share/`, `mansci-enrol/`, `mansci-learning-assistant/`, `mansci-copy-to-my-work/`, `jupyter_server_config.py`, `disable-rtc-document-providers.sh` and the deployed services | Same student/challenge Python modules as local Core; also includes server Jupyter AI and JupyterHub services. ManSci Learning Assistant and the VM `mansci_tools` runner are deployed. The VM persona always uses its centrally configured model and does not offer students a model selector. It guides teams to maintain and critically review one agreed `Team_Project_Context.md` for sustained project work. Teaching Materials notebooks and Team Exchange snapshots open view-only and direct students to Copy to My Work. Students create or join cohort-wide named Team Exchanges and can copy ordinary workspace items except Teaching Materials; teaching staff have oversight access. Notebook and text files use conventional Jupyter saving, with collaborative notebook providers and the Jupyter AI live/server-document providers disabled and locked. The non-document collaboration content token required by Jupyter AI chat remains enabled while all collaboration UI features are disabled. Central teaching files receive versioned pre-save backups. The documented module-lead archive workflow is supported by Ubuntu `unzip`. The HTTPS proxy permits request bodies up to 250 MB for teaching materials and ordinary course data. VM `run_app()` output includes an authenticated classroom URL and credential-free QR code usable by any VM account while the app runs. |
| Student local tools | `distributions/ManSci-Core/payload/environment.yml` and `distributions/ManSci-Lab` | Canonical cross-platform Python package set used by Core, Lab, Spyder, VS Code and Complete. Student ManSci Lab exposes only its packaged Qwen Local Chat persona; it does not discover Staff Lab's ManSci Learning Assistant or the shared environment's Jupyternaut entry point. Its Jupyter AI, router, Persona Manager, LiteLLM adapter and chat versions match Staff Lab so installing either Lab cannot downgrade the other's shared runtime. |
| Staff Lab | `distributions/ManSci-Staff-Lab` | Embeds the current Core and adds Azure configuration, ManSci Learning Assistant and VM-compatible portable Jupyter AI components. Its shared Jupyter AI stack is pinned identically to Student Lab; Staff-only Jupyternaut/tool packages remain additive. |
| GitHub downloads | Six tool ZIPs, the Scenario Week artifact pack and `SHA256SUMS.txt` | Complete, Core, Lab, Spyder, Staff Lab and VS Code are rebuilt from the same installer source; the synchronized teaching pack is attached to the same release. |
| Student environment guidance | `ManSci_AI_Chat_Environment_Context.md` in the Scenario Week pack | Describes VM-first use, local JupyterLab, installed modules, Team Exchange and critical use of `Team_Project_Context.md` for external AI chats. |
| User/support guides | README, Distribution Guide, Staff Lab Guide, Staff Testing | Must state the current application release, Core version and platform-specific limits. |
| Scenario Week teaching assets | Launch deck, Challenge Brief, Coursework Brief, Facilitator Guide and artifact ZIP | Must use current environment names, supported packages, launch routes, Team Exchange, Team Project Context and AI-use guidance. Every generated PowerPoint must be built from `templates/UCL-PowerPoint-Template-UCL-Sans.pptx` and pass `tools/validate_ucl_powerpoint.py`; reproducing only the colours or logo is insufficient. |

## Capability boundaries

Shared across VM and local Core: the `mansci_tools` notebook/console runner, Python 3.13, Management Science Python kernel and the documented challenge modules including Streamlit, Flask, Dash, Gradio, Voilà and jupyter-server-proxy. Dash's optional source-built JupyterLab interface extension is centrally disabled because the supported application runner does not require it.

The VM runner registers each app with the authenticated `mansci-app-share` service and displays an opaque classroom link. Viewers authenticate with their own VM accounts; registration verifies that the loopback port belongs to the presenting account, and the share expires when the app stops or becomes stale. Local installations remain bound to loopback and never display a phone QR code.

VM application logs use a private temporary directory per operating-system user. Do not restore the former shared `/tmp/mansci-app-logs` path.

Staff Lab and VM: ManSci Learning Assistant and the compatible Jupyter AI tool/router components. Staff Lab supplies Azure settings locally and keeps the key in the operating-system credential store.

Both personas require verification of ManSci-specific commands, capabilities and observed results. Unverified claims and illustrative output must be labelled. The VM additionally documents authorised `mansci-enrol MODULE --list` and `--count` operations for module leads.

VM only: JupyterHub accounts, enrolment-specific folders, centrally managed view-only Teaching Materials notebooks, Copy to My Work, and cohort-wide Team Exchange. Students create or join named ad hoc teams and exchange immutable, sender-labelled snapshots from any ordinary workspace location except Teaching Materials; staff have read-only oversight access and do not count towards the configured student limit. Collaborative notebook/document providers, collaboration UI features and Jupyter AI live/server-document providers are disabled and locked because stale document-room state can replace a current server file. The collaboration content-provider token required by the Jupyter AI persona controls remains enabled; it does not replace conventional notebook loading, saving or cell execution. Conventional saves of central teaching files first preserve the existing file beneath `/srv/mansci/teaching-backups`; up to 50 distinct prior versions are retained per file.

The VM HTTPS server block must include `client_max_body_size 250m;`. Validate the complete Nginx configuration before reloading it. JupyterLab uploads use JSON/base64 encoding, so the maximum original file size is lower than the HTTP request-body limit.

Local only: desktop launchers, optional Spyder and VS Code, Ollama/Qwen local chat, and direct localhost application windows. Student ManSci Lab loads Qwen from its own support folder and suppresses every other persona. Staff Lab retains its separate ManSci Learning Assistant and Qwen configuration.

## Change review checklist

1. Identify affected deployment code, manifests and package lists.
2. Identify every guide, release note and teaching asset that describes the changed behaviour.
3. Present the complete proposed change set to Andrew and wait for approval.
4. Apply and test approved changes across each relevant deployment.
5. Rebuild editable documents, reading copies, teaching ZIPs and GitHub release assets.
6. Record versions, exclusions, test results and any required manual checks.
