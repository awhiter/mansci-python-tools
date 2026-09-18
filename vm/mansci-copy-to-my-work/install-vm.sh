#!/usr/bin/env bash
set -euo pipefail

ENV_PREFIX=${ENV_PREFIX:-/opt/miniforge3/envs/mansci-python}
SOURCE_DIR=$(cd "$(dirname "$0")" && pwd)
SITE_PACKAGES=$($ENV_PREFIX/bin/python -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')
LABEXT_DIR=$ENV_PREFIX/share/jupyter/labextensions/@mansci/copy-to-my-work

install -d "$SITE_PACKAGES/mansci_copy_to_my_work" "$LABEXT_DIR" /etc/jupyter
install -m 0644 "$SOURCE_DIR/mansci_copy_to_my_work/__init__.py" "$SITE_PACKAGES/mansci_copy_to_my_work/__init__.py"
install -m 0644 "$SOURCE_DIR/mansci_copy_to_my_work/handlers.py" "$SITE_PACKAGES/mansci_copy_to_my_work/handlers.py"
rm -rf "$LABEXT_DIR/static"
cp -a "$SOURCE_DIR/mansci_copy_to_my_work/labextension/." "$LABEXT_DIR/"
install -m 0644 "$SOURCE_DIR/../jupyter_server_config.py" /etc/jupyter/jupyter_server_config.py

echo "Installed ManSci Copy to My Work 0.2.0. Restart affected user servers to clear existing collaboration rooms."
