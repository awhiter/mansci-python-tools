"""A tool-free local coding assistant for Management Science students."""

from pathlib import Path

import litellm
from jupyter_ai_persona_manager import BasePersona, PersonaDefaults
from jupyterlab_chat.models import Message


class QwenLocalChatPersona(BasePersona):
    """Use Qwen as a conventional chat model without unreliable agent tools."""

    MAX_HISTORY_MESSAGES = 12
    MAX_HISTORY_CHARACTERS = 12_000

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
                "When asked to write code, show the code directly in your response."
            ),
            slash_commands=set(),
        )

    def conversation_messages(self, current: Message) -> list[dict[str, str]]:
        transcript: list[dict[str, str]] = []
        remaining = self.MAX_HISTORY_CHARACTERS
        candidates = [
            item
            for item in self.ychat.get_messages()
            if not item.deleted
            and item.sender in {current.sender, self.id}
            and item.body.strip()
        ]
        if not any(item.id == current.id for item in candidates):
            candidates.append(current)
        for item in reversed(candidates[-self.MAX_HISTORY_MESSAGES :]):
            body = item.body.strip()
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
            num_ctx=16_384,
            stream=True,
        )
        await self.stream_message(stream)

