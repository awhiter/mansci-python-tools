"""Private Jupyter configuration for the student ManSci Lab launcher."""

import sys
from pathlib import Path

distribution_dir = Path(__file__).resolve().parent.parent
if str(distribution_dir) not in sys.path:
    sys.path.insert(0, str(distribution_dir))
from mansci_student_persona_guard import install as install_student_persona_guard

install_student_persona_guard()

c = get_config()  # noqa: F821 - supplied by Jupyter when loading this file
c.KernelSpecManager.ensure_native_kernel = False
c.KernelSpecManager.allowed_kernelspecs = {"mansci-python"}
c.ServerApp.ip = "127.0.0.1"
c.ServerApp.open_browser = True
c.ServerApp.use_redirect_file = False
c.ServerApp.allow_remote_access = False
c.ServerApp.quit_button = True
c.PersonaManager.default_persona_id = (
    "jupyter-ai-personas::qwen_local_persona::QwenLocalChatPersona"
)
c.PersonaManager.builtin_mcp_servers = []
c.ServerApp.jpserver_extensions = {"jupyter_server_mcp": False}
