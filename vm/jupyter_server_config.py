"""ManSci VM Jupyter Server settings."""

c = get_config()  # noqa: F821 - supplied by Jupyter's configuration loader

# Discard inactive collaborative documents promptly. Protected Teaching Materials
# cannot be saved, so retaining an unsaved in-memory copy only confuses students.
c.YRoomManager.auto_free_interval = 15
