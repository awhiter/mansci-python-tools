# ManSci Copy to My Work

This VM-only JupyterLab extension copies centrally managed teaching files into a student's writable `My Work` area. Version 0.2 also makes notebooks opened directly beneath `Teaching Materials` visibly view-only and prevents a kernel being started for them.

The prebuilt labextension is stored with the source so the VM deployment does not need Node.js. Install the Python server package and copy `mansci_copy_to_my_work/labextension` to the environment's JupyterLab labextensions directory.

Do not retain a backup beneath `share/jupyter/labextensions/@mansci/`. JupyterLab scans every directory there and may let an old backup manifest override the live extension. The installation script moves the known legacy backup to `/var/backups/mansci-jupyterlab-extensions` before installing.
