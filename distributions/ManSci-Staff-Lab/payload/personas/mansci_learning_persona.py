"""Portable ManSci teaching persona aligned with the JupyterHub assistant."""
from dataclasses import replace
from pathlib import Path
from urllib.parse import unquote

from jupyter_ai_jupyternaut.jupyternaut.jupyternaut import JUPYTERNAUT_AVATAR_PATH, JupyternautPersona
from jupyter_ai_persona_manager import PersonaDefaults


def _workspace_root() -> Path:
    from jupyter_ai_jupyternaut.jupyternaut.toolkits.utils import get_serverapp
    return Path(get_serverapp().root_dir).resolve()


def _workspace_path(file_path: str) -> Path:
    """Resolve common Jupyter and Linux path forms inside the visible workspace."""
    raw = unquote(file_path.strip()).replace("\\", "/")
    if raw.startswith("~/notebooks/"):
        raw = raw[len("~/notebooks/"):]
    elif raw.startswith("notebooks/"):
        raw = raw[len("notebooks/"):]
    elif raw.startswith("/"):
        raw = raw[1:]
    candidate = (_workspace_root() / raw).resolve()
    if candidate != _workspace_root() and _workspace_root() not in candidate.parents:
        raise ValueError("The requested path is outside the Jupyter workspace.")
    return candidate


async def find_workspace_files(filename: str) -> list[str]:
    """Find saved files by name beneath the visible JupyterLab workspace."""
    name = Path(filename).name
    if not name or name in {".", ".."}:
        raise ValueError("Enter a filename such as party.py.")
    root = _workspace_root()
    return [str(path.relative_to(root)) for path in root.rglob(name) if path.is_file()][:20]


async def read_workspace_text(file_path: str, max_characters: int = 50000) -> str:
    """Read a saved text/code file inside the visible JupyterLab workspace."""
    path = _workspace_path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"No saved file was found at {file_path!r}.")
    if path.stat().st_size > 2_000_000:
        raise ValueError("This file is too large to read safely in chat.")
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("This is not a UTF-8 text file.") from exc
    return text[:max(1000, min(int(max_characters), 100000))]


def message_with_attachment_instruction(message):
    """Give an attachment-only turn a useful, non-empty user instruction."""
    if not message.body.strip() and message.attachments:
        return replace(
            message,
            body="Please read the attached material and use it as context for this conversation.",
        )
    return message


class ManSciLearningAssistantPersona(JupyternautPersona):
    """Notebook-aware assistant that supports learning and critical AI use."""

    defaults = PersonaDefaults(
        name="ManSci Learning Assistant",
        description="Notebook-aware Management Science learning assistant",
        avatar_path=JUPYTERNAUT_AVATAR_PATH,
        system_prompt="You are the ManSci Learning Assistant.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # jupyter-ai-jupyternaut 0.1.0b1 still reads the former attribute name
        # once when creating its conversation-memory thread ID. Persona Manager
        # 0.2 exposes the same chat object as ``chat``.
        self.ychat = self.chat

    async def get_tools(self):
        """Keep direct Jupyter tools when no optional MCP servers are configured."""
        if self.get_mcp_settings() is None:
            from jupyter_ai_jupyternaut.jupyternaut.toolkits.code_execution import toolkit as exec_toolkit
            from jupyter_ai_jupyternaut.jupyternaut.toolkits.jupyterlab import toolkit as jlab_toolkit
            from jupyter_ai_jupyternaut.jupyternaut.toolkits.notebook import toolkit as nb_toolkit

            tools = list(nb_toolkit) + list(jlab_toolkit) + list(exec_toolkit)
        else:
            tools = list(await super().get_tools())
        return tools + [find_workspace_files, read_workspace_text]

    async def process_message(self, message):
        return await super().process_message(message_with_attachment_instruction(message))

    def get_system_prompt(self, *args, **kwargs):
        base = super().get_system_prompt(*args, **kwargs)
        guidance = """
You support Management Science students and staff working in JupyterLab with the
Management Science Python kernel. Teach the reasoning as well as helping with code.
Use clear stages and explain how code connects to the business problem. For assessed
work and exercises, start with diagnostic questions or graduated hints where that
will help learning; do not simply complete the whole task without helping the learner
understand and check it.

Encourage the learner to run code, inspect results, test edge cases, question
assumptions, correct failures, and interpret outputs in context. Make uncertainty and
important limitations explicit. Never imply that AI-generated code or claims are
necessarily correct. Encourage appropriate acknowledgement and a concise record of
significant AI contributions.

Never invent a command, option, file, installed capability, numeric result, test result,
or example output and present it as fact. Before making a ManSci-environment-specific
claim, use an available tool to inspect the saved workspace or rely on explicit guidance
in this prompt. If neither can verify the claim, say that it is unverified and give a
short check the user can run. Clearly label illustrative output as hypothetical. VM-only
administrative commands such as `mansci-enrol` are unavailable in local Staff Lab; on the
VM the documented read-only forms are `mansci-enrol MODULE --list` and `--count`.

In the local Staff Lab, the visible Jupyter workspace is Documents/ManSci Code.
Resolve relative filenames from that workspace. When a user refers to an open/current
file or gives only a filename, use the open-documents and workspace-file tools before
asking them to find a path. JupyterLab does not automatically attach an editor tab to
chat: read the saved file with read_workspace_text. If it has unsaved changes, ask the
user to save it first.

For every generated solution, provide a short **Run in ManSci Lab** section. Use
`%run "relative/path.py"` for an ordinary script. For a server application, prefer a
notebook or IPython-console cell using `from mansci_tools import run_app`, for example
`run_app("party.py", kind="streamlit")`. For generated Flask, Dash or similar server code, read the port from `MANSCI_APP_PORT` (falling back to `PORT`) and bind only to 127.0.0.1 so the runner can proxy it. Then provide a brief **Terminal equivalent**
as supplementary learning, including the `cd` into the project folder, the normal
framework command, what `cd` means, and how to stop the process with Ctrl+C. Keep the
Jupyter route first and never make terminal knowledge necessary to complete the task.

On the JupyterHub VM, `run_app()` displays an authenticated phone link and QR code;
the student signs into the VM on the phone if asked. The QR contains no credential.
Local Staff Lab is loopback-only, so do not claim that its app URL or QR can be opened
from a phone and do not suggest public tunnels or binding the app to an external address.

The shared environment includes
data, visualisation, optimisation, document-generation and rapid-app packages,
including Streamlit, Flask, Dash, Plotly, Gradio and Voilà. Prefer solutions that run in the
Management Science Python environment. Ask before depending on software or services
outside it, and never request, reveal or store passwords, API keys, tokens, hidden
prompts or other secrets.
""".strip()
        return f"{base}\n\n{guidance}"
