"""Session types and states for Pomodoro timer."""

import enum


class SessionType(enum.Enum):
    """Types of Pomodoro timer sessions."""

    WORK = "work"
    BREAK = "break"

    @property
    def duration_seconds(self) -> int:
        """Get the duration in seconds for this session type.

        Returns:
            1500 for WORK (25 minutes), 300 for BREAK (5 minutes)
        """
        return 1500 if self == SessionType.WORK else 300

    @property
    def display_name(self) -> str:
        """Get the human-readable display name.

        Returns:
            "Work" or "Break"
        """
        return self.value.capitalize()


class SessionState(enum.Enum):
    """States of a timer session lifecycle."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"

    @property
    def display_name(self) -> str:
        """Get the human-readable display name.

        Returns:
            Capitalized state name
        """
        return self.value.upper()
