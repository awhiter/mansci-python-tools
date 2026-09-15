"""Portable ManSci teaching persona aligned with the JupyterHub assistant."""
from dataclasses import replace

from jupyter_ai_jupyternaut.jupyternaut.jupyternaut import JUPYTERNAUT_AVATAR_PATH, JupyternautPersona
from jupyter_ai_persona_manager import PersonaDefaults


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

            return list(nb_toolkit) + list(jlab_toolkit) + list(exec_toolkit)
        return await super().get_tools()

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

The usual working folder is Documents/ManSci Code. The shared environment includes
data, visualisation, optimisation, document-generation and rapid-app packages,
including Streamlit, Plotly, Gradio and Voilà. Prefer solutions that run in the
Management Science Python environment. Ask before depending on software or services
outside it, and never request, reveal or store passwords, API keys, tokens, hidden
prompts or other secrets.
""".strip()
        return f"{base}\n\n{guidance}"
