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

# Browser sessions need access to the shared-preview service, and the narrow
# API token issued to each single-user server needs the same service scope so
# run_app() can register and revoke links. Retain the standard default scopes.
c.JupyterHub.load_roles = [
    {
        "name": "user",
        "scopes": ["self", "access:services!service=mansci-app-share"],
    },
    {
        "name": "server",
        "scopes": [
            "users:activity!user",
            "access:servers!server",
            "access:services!service=mansci-app-share",
        ],
    },
]
c.Spawner.server_token_scopes = [
    "users:activity!user",
    "access:servers!server",
    "access:services!service=mansci-app-share",
]
