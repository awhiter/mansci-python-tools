#!/usr/bin/env bash
set -euo pipefail

ENV_PREFIX=${ENV_PREFIX:-/opt/miniforge3/envs/mansci-python}
SOURCE_DIR=$(cd "$(dirname "$0")" && pwd)
SITE_PACKAGES=$($ENV_PREFIX/bin/python -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')
LABEXT_DIR=$ENV_PREFIX/share/jupyter/labextensions/@mansci/copy-to-my-work
LEGACY_BACKUP=$ENV_PREFIX/share/jupyter/labextensions/@mansci/copy-to-my-work.backup-0.1.1

install -d "$SITE_PACKAGES/mansci_copy_to_my_work" "$LABEXT_DIR" /etc/jupyter /etc/mansci /usr/local/libexec /srv/mansci/team-exchange/files
# JupyterLab scans every directory beneath an extension scope. A backup left
# beside the live package can therefore override the current manifest.
if [[ -d "$LEGACY_BACKUP" ]]; then
  install -d /var/backups/mansci-jupyterlab-extensions
  mv "$LEGACY_BACKUP" /var/backups/mansci-jupyterlab-extensions/
fi
install -m 0644 "$SOURCE_DIR/mansci_copy_to_my_work/__init__.py" "$SITE_PACKAGES/mansci_copy_to_my_work/__init__.py"
install -m 0644 "$SOURCE_DIR/mansci_copy_to_my_work/handlers.py" "$SITE_PACKAGES/mansci_copy_to_my_work/handlers.py"
install -o root -g root -m 0755 "$SOURCE_DIR/mansci-team-exchange-backend" /usr/local/libexec/mansci-team-exchange-backend
if [[ ! -f /etc/mansci/team-exchange.conf ]]; then
  cat > /etc/mansci/team-exchange.conf <<'EOF'
# MODULE|MAXIMUM_STUDENT_TEAM_SIZE
MSIN0023|6
EOF
fi
chown root:root /etc/mansci/team-exchange.conf
chmod 0644 /etc/mansci/team-exchange.conf
cat > /etc/sudoers.d/mansci-team-exchange <<'EOF'
ALL ALL=(root) NOPASSWD: /usr/local/libexec/mansci-team-exchange-backend
EOF
chmod 0440 /etc/sudoers.d/mansci-team-exchange
visudo -cf /etc/sudoers.d/mansci-team-exchange
chown root:root /srv/mansci/team-exchange
chmod 0711 /srv/mansci/team-exchange /srv/mansci/team-exchange/files
rm -rf "$LABEXT_DIR/static"
cp -a "$SOURCE_DIR/mansci_copy_to_my_work/labextension/." "$LABEXT_DIR/"
install -m 0644 "$SOURCE_DIR/../jupyter_server_config.py" /etc/jupyter/jupyter_server_config.py

echo "Installed ManSci Copy to My Work and Team Exchange 0.3.0. Restart affected user servers to load the current workflow."
