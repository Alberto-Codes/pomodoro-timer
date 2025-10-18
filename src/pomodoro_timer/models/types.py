"""Session types and states for Pomodoro timer."""

import enum


class SessionDurations:
    """Configurable durations for session types."""
    
    work_duration_seconds: int = 1500  # 25 minutes default
    break_duration_seconds: int = 300  # 5 minutes default


class SessionType(enum.Enum):
    """Types of Pomodoro timer sessions."""

    WORK = "work"
    BREAK = "break"

    @property
    def duration_seconds(self) -> int:
        """Get the duration in seconds for this session type.

        Returns:
            Configured duration from SessionDurations
        """
        if self == SessionType.WORK:
            return SessionDurations.work_duration_seconds
        else:
            return SessionDurations.break_duration_seconds

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
