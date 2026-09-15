# ManSci deployment and asset synchronization record

Current coordinated release: **2026.09.15.6**
Shared Python Core: **2026.09.15.2**

Review this record before proposing or approving a change. Do not change a listed deployment or asset until Andrew has approved the cross-asset change set.

| Area | Canonical asset | Current relationship |
|---|---|---|
| JupyterHub VM Python | `mansci-python-server.yml` and deployed `mansci-python` environment | Same student/challenge Python modules as local Core; also includes server Jupyter AI and JupyterHub services. |
| Student local tools | `distributions/ManSci-Core/payload/environment.yml` | Canonical cross-platform Python package set used by Core, Lab, Spyder, VS Code and Complete. |
| Staff Lab | `distributions/ManSci-Staff-Lab` | Embeds the current Core and adds Azure configuration, ManSci Learning Assistant and VM-compatible portable Jupyter AI components. |
| GitHub downloads | Six ZIPs plus `SHA256SUMS.txt` | Complete, Core, Lab, Spyder, Staff Lab and VS Code are rebuilt from the same installer source. |
| Student environment guidance | `ManSci_AI_Chat_Environment_Context.md` in the Scenario Week pack | Describes VM-first use, local JupyterLab, installed modules and learning guidance for external AI chats. |
| User/support guides | README, Distribution Guide, Staff Lab Guide, Staff Testing | Must state the current application release, Core version and platform-specific limits. |
| Scenario Week teaching assets | Launch deck, Challenge Brief, Coursework Brief, Facilitator Guide and artifact ZIP | Must use current environment names, supported packages, launch routes and AI-use guidance. |

## Capability boundaries

Shared across VM and local Core: Python 3.13, Management Science Python kernel and the documented challenge modules including Streamlit, Gradio, Voilà and jupyter-server-proxy.

Staff Lab and VM: ManSci Learning Assistant and the compatible Jupyter AI tool/router components. Staff Lab supplies Azure settings locally and keeps the key in the operating-system credential store.

VM only: JupyterHub accounts, enrolment-specific folders, centrally managed Teaching Materials and Copy to My Work.

Local only: desktop launchers, optional Spyder and VS Code, Ollama/Qwen local chat, and direct localhost application windows.

## Change review checklist

1. Identify affected deployment code, manifests and package lists.
2. Identify every guide, release note and teaching asset that describes the changed behaviour.
3. Present the complete proposed change set to Andrew and wait for approval.
4. Apply and test approved changes across each relevant deployment.
5. Rebuild editable documents, reading copies, teaching ZIPs and GitHub release assets.
6. Record versions, exclusions, test results and any required manual checks.
