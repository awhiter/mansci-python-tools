"""Restrict the student ManSci Lab to its packaged local Qwen persona."""

from __future__ import annotations

from pathlib import Path


_INSTALLED = False


def install() -> None:
    """Use the Lab-specific persona directory and suppress package personas."""
    global _INSTALLED
    if _INSTALLED:
        return

    from jupyter_ai_persona_manager.persona_manager import (
        PersonaManager,
        load_from_dir,
    )

    persona_dir = Path(__file__).resolve().parent / "personas"

    def load_no_entry_point_personas(self) -> None:
        # Staff Lab installs Jupyternaut into the shared Python environment.
        # The student Lab intentionally offers only its private local model.
        PersonaManager._ep_persona_classes = []

    def load_student_persona(self) -> None:
        # Do not inspect Documents/ManSci Code/.jupyter/personas: that workspace
        # is shared with Staff Lab and can contain its Azure-backed persona.
        self._local_persona_classes = load_from_dir(str(persona_dir), self.log)

    PersonaManager._init_ep_persona_classes = load_no_entry_point_personas
    PersonaManager._init_local_persona_classes = load_student_persona
    PersonaManager._ep_persona_classes = []
    _INSTALLED = True
