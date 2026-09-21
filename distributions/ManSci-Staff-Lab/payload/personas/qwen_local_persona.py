"""A local coding assistant with bounded, read-only workspace context."""

import json
import re
from pathlib import Path

import litellm
from jupyter_ai_persona_manager import BasePersona, PersonaDefaults
from jupyterlab_chat.models import Message


def _chat_document(persona):
    """Return the chat document across Persona Manager 0.1 and 0.2."""
    return getattr(persona, "chat", None) or getattr(persona, "ychat")


def _local_context() -> str:
    """Load the compact, local-only ManSci Lab guidance packaged with Qwen."""
    return Path(__file__).with_name("qwen_local_context.md").read_text(encoding="utf-8")


SUPPORTED_TEXT_SUFFIXES = {
    ".csv", ".ini", ".ipynb", ".json", ".md", ".py", ".r", ".rst",
    ".toml", ".tsv", ".txt", ".yaml", ".yml",
}
FILE_REFERENCE_RE = re.compile(
    r"(?<![\w])(?:~?/)?(?:[\w.-]+/)*[\w.-]+\.(?:csv|ini|ipynb|json|md|py|r|rst|toml|tsv|txt|ya?ml)\b",
    re.IGNORECASE,
)


def _workspace_root(persona) -> Path:
    """Return the Jupyter contents root supplied by Persona Manager."""
    return Path(persona.parent.root_dir).expanduser().resolve()


def _safe_workspace_path(root: Path, value: str) -> Path:
    """Resolve a Jupyter path while preventing access outside its workspace."""
    raw = value.strip().replace("\\", "/")
    if raw.startswith("~/"):
        raw = raw[2:]
    candidate = (root / raw.lstrip("/")).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("path is outside the ManSci workspace")
    return candidate


def _notebook_text(path: Path) -> str:
    """Render notebook source cells as compact text rather than raw JSON."""
    notebook = json.loads(path.read_text(encoding="utf-8"))
    sections = []
    for index, cell in enumerate(notebook.get("cells", []), start=1):
        kind = cell.get("cell_type", "cell")
        source = cell.get("source", "")
        if isinstance(source, list):
            source = "".join(source)
        if str(source).strip():
            sections.append(f"--- {kind} cell {index} ---\n{source}")
    return "\n\n".join(sections)


def _read_workspace_text(root: Path, path: Path, limit: int) -> tuple:
    """Read a supported saved text file, returning content or a clear reason."""
    if path != root and root not in path.parents:
        return None, "is outside the ManSci workspace"
    if not path.is_file():
        return None, "was not found as a saved file"
    if path.suffix.lower() not in SUPPORTED_TEXT_SUFFIXES:
        return None, "is not a supported text, code or notebook file"
    if path.stat().st_size > 2_000_000:
        return None, "is too large to read safely"
    try:
        text = _notebook_text(path) if path.suffix.lower() == ".ipynb" else path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, json.JSONDecodeError, OSError):
        return None, "could not be read as UTF-8 text"
    if "\x00" in text:
        return None, "appears to be a binary file"
    if len(text) > limit:
        text = text[:limit] + "\n[File content truncated by ManSci Lab]"
    return text, None


def _referenced_paths(root: Path, body: str) -> tuple[list[Path], list[str]]:
    """Resolve unambiguous saved filenames explicitly mentioned by the user."""
    resolved, notices = [], []
    values = list(dict.fromkeys(match.group(0) for match in FILE_REFERENCE_RE.finditer(body)))
    for value in values:
        try:
            if "/" in value or value.startswith("~"):
                matches = [_safe_workspace_path(root, value)]
            else:
                matches = [p for p in root.rglob(value) if p.is_file() and not any(part.startswith(".") for part in p.relative_to(root).parts)]
        except ValueError as exc:
            notices.append(f"{value}: {exc}")
            continue
        if len(matches) == 1:
            resolved.append(matches[0])
        elif not matches:
            notices.append(f"{value}: no saved file was found")
        else:
            choices = ", ".join(str(p.relative_to(root)) for p in matches[:5])
            notices.append(f"{value}: several files match ({choices}); ask which one is intended")
    return resolved, notices


def _message_content(persona, message, file_budget: int) -> str:
    """Add bounded attachment and referenced-file content to a user message."""
    body = message.body.strip()
    root = _workspace_root(persona)
    chat = _chat_document(persona)
    paths, notices = [], []
    attachments = chat.get_attachments()
    for attachment_id in message.attachments or []:
        attachment = attachments.get(attachment_id)
        if attachment is None:
            notices.append("an attached item could not be resolved")
            continue
        try:
            paths.append(_safe_workspace_path(root, attachment.value))
        except ValueError as exc:
            notices.append(f"{attachment.value}: {exc}")
    referenced, reference_notices = _referenced_paths(root, body)
    paths.extend(referenced)
    notices.extend(reference_notices)
    unique_paths = list(dict.fromkeys(paths))
    context = []
    remaining = file_budget
    for path in unique_paths:
        if remaining <= 0:
            notices.append("additional file context was omitted because the local-model limit was reached")
            break
        text, error = _read_workspace_text(root, path, min(8_000, remaining))
        label = str(path.relative_to(root)) if path == root or root in path.parents else path.name
        if error:
            notices.append(f"{label}: {error}")
            continue
        block = f"\n\n[Saved ManSci workspace file: {label}]\n{text}\n[End file: {label}]"
        context.append(block)
        remaining -= len(block)
    if notices:
        context.append("\n\n[ManSci file-context notes: " + "; ".join(notices) + "]")
    if not body and unique_paths:
        body = "Please use the attached saved material as context."
    return body + "".join(context)


class QwenLocalChatPersona(BasePersona):
    """Use Qwen as a conventional chat model without unreliable agent tools."""

    MAX_HISTORY_MESSAGES = 12
    MAX_HISTORY_CHARACTERS = 12_000
    MAX_FILE_CONTEXT_CHARACTERS = 12_000

    @property
    def defaults(self) -> PersonaDefaults:
        return PersonaDefaults(
            name="Qwen Local Chat",
            description="A private, local coding assistant powered by Qwen2.5-Coder 3B.",
            avatar_path=str(Path(__file__).with_name("qwen-local.svg")),
            system_prompt=(
                "You are a concise Python teaching assistant for Management Science. "
                "Users may paste raw code directly into chat, with or without an explanation. "
                "Recognise pasted source code automatically and never require the user to add "
                "Markdown fences, backticks, labels, or other formatting. If the request is "
                "implicit, briefly explain what the pasted code does and point out likely issues. "
                "Answer in clear Markdown and put runnable code in fenced code blocks. "
                "Do not emit tool calls, function-call JSON, or claim to edit notebooks. "
                "When asked to write code, show the code directly in your response. "
                "ManSci Lab may add bounded contents from saved attached or explicitly named "
                "workspace files. Treat those labelled blocks as user-provided context. Open "
                "editor tabs and unsaved changes are not visible; ask the user to save first.\n\n"
                + _local_context()
            ),
            slash_commands=set(),
        )

    def conversation_messages(self, current: Message) -> list[dict[str, str]]:
        transcript: list[dict[str, str]] = []
        remaining = self.MAX_HISTORY_CHARACTERS
        # Persona Manager 0.1 calls this ``ychat``; 0.2 calls it ``chat``.
        chat_document = _chat_document(self)
        candidates = [
            item
            for item in chat_document.get_messages()
            if not item.deleted
            and item.sender in {current.sender, self.id}
            and (item.body.strip() or item.attachments)
        ]
        if not any(item.id == current.id for item in candidates):
            candidates.append(current)
        for item in reversed(candidates[-self.MAX_HISTORY_MESSAGES :]):
            body = (
                _message_content(self, item, self.MAX_FILE_CONTEXT_CHARACTERS)
                if item.sender != self.id
                else item.body.strip()
            )
            if len(body) > remaining:
                if transcript:
                    break
                body = body[:remaining]
            transcript.append(
                {"role": "assistant" if item.sender == self.id else "user", "content": body}
            )
            remaining -= len(body)
            if remaining <= 0:
                break
        transcript.reverse()
        return transcript

    async def process_message(self, message: Message) -> None:
        stream = await litellm.acompletion(
            model="ollama/qwen2.5-coder:3b",
            api_base="http://127.0.0.1:11434",
            messages=[
                {"role": "system", "content": self.system_prompt},
                *self.conversation_messages(message),
            ],
            num_ctx=8_192,
            max_tokens=1536,
            temperature=0.1,
            keep_alive="15m",
            stream=True,
        )
        await self.stream_message(stream)
