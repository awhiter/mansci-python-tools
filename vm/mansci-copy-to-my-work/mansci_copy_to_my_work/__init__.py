from .handlers import setup_handlers

__version__ = "0.2.0"


def _jupyter_server_extension_points():
    return [{"module": "mansci_copy_to_my_work"}]


def _load_jupyter_server_extension(server_app):
    setup_handlers(server_app.web_app)
