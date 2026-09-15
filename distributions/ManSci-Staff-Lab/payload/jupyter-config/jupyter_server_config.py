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
