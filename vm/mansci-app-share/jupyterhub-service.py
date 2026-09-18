# Merge into jupyterhub_config.py. JupyterHub supplies the service with its
# OAuth client and API token environment. Every authenticated Hub account may
# view a valid temporary share; the service itself validates ownership/expiry.
c.JupyterHub.services = [
    {
        "name": "mansci-app-share",
        "url": "http://127.0.0.1:8999",
        "command": [
            "/opt/jupyterhub/bin/python",
            "/usr/local/lib/mansci-app-share/service.py",
        ],
        "oauth_no_confirm": True,
    }
]
