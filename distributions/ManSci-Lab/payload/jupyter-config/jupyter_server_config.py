"""Private Jupyter configuration for the student ManSci Lab launcher."""

c = get_config()  # noqa: F821 - supplied by Jupyter when loading this file
c.KernelSpecManager.ensure_native_kernel = False
c.KernelSpecManager.allowed_kernelspecs = {"mansci-python"}
c.ServerApp.ip = "127.0.0.1"
c.ServerApp.open_browser = True
c.ServerApp.use_redirect_file = False
c.ServerApp.allow_remote_access = False
c.ServerApp.quit_button = True
