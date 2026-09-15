"""Private configuration used only by the ManSci Staff Lab launcher."""

import sys
from pathlib import Path

# Load the distribution's safety guard before the persona extensions create
# their room managers. The package is pinned, so this guard is deliberately
# scoped to Staff Lab rather than altering the conda installation itself.
distribution_dir = Path(__file__).resolve().parent.parent
if str(distribution_dir) not in sys.path:
    sys.path.insert(0, str(distribution_dir))
from mansci_jupyter_ai_guard import install as install_mansci_jupyter_ai_guard

install_mansci_jupyter_ai_guard()

c = get_config()  # noqa: F821

# Show only the explicitly registered Management Science kernel.  JupyterLab
# itself is also launched from that environment.
c.KernelSpecManager.ensure_native_kernel = False
c.KernelSpecManager.allowed_kernelspecs = {"mansci-python"}

# Local access only. Jupyter still creates its normal random authentication
# token and opens the user's browser.
c.ServerApp.ip = "127.0.0.1"
c.ServerApp.open_browser = False
c.ServerApp.allow_remote_access = False
c.ServerApp.quit_button = True

# Jupyter AI 3.2's packaged fallback still points to the retired jupyter_ai
# persona ID. Select the local ManSci subclass explicitly so a new chat is
# immediately usable.
c.PersonaManager.default_persona_id = (
    "jupyter-ai-personas::mansci_learning_persona::ManSciLearningAssistantPersona"
)

# Jupyternaut already has its notebook, execution and JupyterLab tools. The
# separate MCP HTTP listener is unnecessary on a single-user local Staff Lab
# and its fixed port can collide with another Jupyter process.
c.PersonaManager.builtin_mcp_servers = []
c.ServerApp.jpserver_extensions = {"jupyter_server_mcp": False}
