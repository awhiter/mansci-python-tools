# ManSci VS Code — Student Guide

Always start this teaching setup from **ManSci VS Code** on your Desktop. It is separate from your ordinary VS Code settings, automatically uses the `mansci-python` environment, and opens your `Documents/ManSci Code` folder.

## Python files with cells

Divide a Python file into cells with `# %%`:

```python
# %%
import pandas as pd

# %%
data = pd.DataFrame({"value": [1, 2, 3]})
data.describe()
```

Click **Run Cell** above a cell, or put the cursor in it and press Shift+Enter. Results appear in the Interactive Window. Use the Run button to run a complete Python file.

## Notebooks

The starting folder contains **New ManSci Notebook.ipynb**. It already names the **Management Science Python** kernel, so make a copy of it when starting a notebook.

The ManSci launcher assigns Python notebooks in the ManSci Code folder to **Management Science Python** automatically. Notebook results appear directly underneath the notebook cell. They do not appear in the separate Interactive Window, which is used by `# %%` cells in `.py` files.

If a notebook was already open while the installer was running, close and reopen ManSci VS Code before using it.

## Local AI chat

Open **Continue** from its icon in the Activity Bar, or press Ctrl+L on Windows / Cmd+L on macOS. The configured **Qwen2.5-Coder 3B** model runs locally through Ollama, needs no account or shared key, and remembers the conversation within a chat session. It assumes that coding requests mean Python unless you explicitly name another language. You can add the open file, selected code or other workspace files as context from the Continue controls.

The first time Continue opens it may show a **Continue Hub** welcome card. You do not need to log in: close the card using its **X**, and the local Qwen model will be available. This choice is remembered.

For an embedded edit, save the file, select the complete function or logical block you want changed, then press Ctrl+I on Windows / Cmd+I on macOS. The assistant is instructed to consider the surrounding code and make the smallest compatible change. If related definitions are in another file, add that file to the prompt's context. Continue can also offer local, grey-text completions while typing; press Tab to accept one or Escape to dismiss it. The ordinary VS Code/Copilot Chat controls are hidden because they require a GitHub account and are not part of this teaching setup.

This small model is intended for demonstrations and straightforward explanations or code generation. Review and run generated code rather than assuming it is correct. Autonomous Agent mode is deliberately disabled: use Ask/Edit-style chat and review changes before accepting them.

The Continue panel should open directly with **Qwen2.5-Coder 3B**. It should not request a model key. If it shows an add-model or API-key form, close ManSci VS Code completely and rerun the latest installer; this repairs the pinned Continue version and local configuration. If Ollama is not installed, install it from [ollama.com/download](https://ollama.com/download) and rerun the installer.

## Files and workspace

The default starting folder is:

- Windows: `Documents\ManSci Code`
- macOS: `Documents/ManSci Code`

To use a different shared folder, edit `ManSci Code Home.txt` in Documents, put the full folder path on its only line, save it, and restart ManSci VS Code.

## Checking the setup

Run `student-profile-check.py` from the shared folder. All lines should say PASS. The old **ManSci Check** and **ManSci VS Code Check** desktop launchers have been retired; use **ManSci Help** for guidance and send this script's output to staff when requested.

If the interpreter shown at the bottom of VS Code is not `mansci-python`, close ManSci VS Code and rerun the installer. Do not import another profile into this isolated instance.
