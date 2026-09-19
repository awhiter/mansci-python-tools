#!/usr/bin/env bash
set -euo pipefail

ENV_PREFIX=${ENV_PREFIX:-/opt/miniforge3/envs/mansci-python}

"$ENV_PREFIX/bin/jupyter" labextension disable \
  '@jupyter/docprovider-extension:ynotebook' --level=sys_prefix
"$ENV_PREFIX/bin/jupyter" labextension disable \
  '@jupyter/docprovider-extension:yfile' --level=sys_prefix
"$ENV_PREFIX/bin/jupyter" labextension disable \
  '@jupyter-ai-contrib/server-documents:server-cell-executor' --level=sys_prefix
"$ENV_PREFIX/bin/jupyter" labextension disable \
  '@jupyter-ai-contrib/server-documents' --level=sys_prefix
"$ENV_PREFIX/bin/jupyter" labextension disable \
  '@jupyter-ai-contrib/live-content' --level=sys_prefix
"$ENV_PREFIX/bin/jupyter" labextension lock \
  '@jupyter/docprovider-extension:ynotebook' --level=sys_prefix
"$ENV_PREFIX/bin/jupyter" labextension lock \
  '@jupyter/docprovider-extension:yfile' --level=sys_prefix
"$ENV_PREFIX/bin/jupyter" labextension lock \
  '@jupyter-ai-contrib/server-documents:server-cell-executor' --level=sys_prefix
"$ENV_PREFIX/bin/jupyter" labextension lock \
  '@jupyter-ai-contrib/server-documents' --level=sys_prefix
"$ENV_PREFIX/bin/jupyter" labextension lock \
  '@jupyter-ai-contrib/live-content' --level=sys_prefix

# The collaboration package disables JupyterLab's normal cell executor because
# it supplies its own. Restore the normal executor after disabling that
# replacement; false overrides the package-level disabledExtensions entry.
ENV_PREFIX="$ENV_PREFIX" "$ENV_PREFIX/bin/python" - <<'PY'
import json
import os
from pathlib import Path

path = Path(os.environ["ENV_PREFIX"]) / "etc/jupyter/labconfig/page_config.json"
data = json.loads(path.read_text()) if path.exists() else {}
executor = "@jupyterlab/notebook-extension:cell-executor"
data.setdefault("disabledExtensions", {})[executor] = False
data.setdefault("lockedExtensions", {})[executor] = True
temporary = path.with_suffix(".json.tmp")
temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
temporary.chmod(0o644)
temporary.replace(path)
PY

echo "Disabled collaborative/live document providers and restored conventional saving and cell execution."
