"""Safety guards for the pinned Jupyter AI/Jupyternaut staff distribution.

JupyterLab Chat is based on a real-time Yjs document. Under some update orders,
the same user message can be observed more than once. Jupyternaut 0.1.0b1 does
not deduplicate those observations before scheduling model calls. This module
adds that missing boundary guard and gives SQLite a sensible lock wait.
"""

from __future__ import annotations

from collections import deque


_INSTALLED = False
_MAX_SEEN_MESSAGE_IDS = 2000


def install() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    from jupyter_ai_persona_manager.persona_manager import PersonaManager
    from jupyter_ai_jupyternaut.jupyternaut import jupyternaut as jn

    original_route = PersonaManager.on_chat_message

    def guarded_route(self, room_id, message):
        # Record before scheduling the asynchronous handler. Several Yjs
        # notifications can arrive in one event-loop turn, so checking inside
        # process_message() is too late to prevent concurrent Azure calls.
        message_id = getattr(message, "id", None)
        if not message_id:
            return original_route(self, room_id, message)

        seen = getattr(self, "_mansci_seen_message_ids", None)
        order = getattr(self, "_mansci_seen_message_order", None)
        if seen is None or order is None:
            seen = set()
            order = deque()
            self._mansci_seen_message_ids = seen
            self._mansci_seen_message_order = order

        if message_id in seen:
            self.log.warning("Ignored duplicate chat event for message %s", message_id)
            return None

        seen.add(message_id)
        order.append(message_id)
        while len(order) > _MAX_SEEN_MESSAGE_IDS:
            seen.discard(order.popleft())
        return original_route(self, room_id, message)

    async def create_memory_store_with_timeout(self):
        try:
            import aiosqlite
            from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
        except ImportError:
            from langgraph.checkpoint.memory import InMemorySaver
            return InMemorySaver()

        conn = await aiosqlite.connect(
            jn.MEMORY_STORE_PATH,
            timeout=30,
            check_same_thread=False,
        )
        await conn.execute("PRAGMA busy_timeout=30000")
        await conn.execute("PRAGMA journal_mode=WAL")
        await conn.commit()
        return AsyncSqliteSaver(conn)

    PersonaManager.on_chat_message = guarded_route
    jn.JupyternautPersona._create_memory_store = create_memory_store_with_timeout
    _INSTALLED = True
