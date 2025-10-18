"""Data models for UI layer.

This module defines UI-specific data models that complement the existing timer models.
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime

from pomodoro_timer.models.session import TimerSession
from pomodoro_timer.models.types import SessionType


@dataclass
class CompletedSession:
    """Represents a completed Pomodoro session for history display.

    Attributes:
        id: Database ID (None if not yet persisted)
        session_type: Type of completed session (WORK or BREAK)
        start_time: When session started (datetime object)
        end_time: When session ended (datetime object)
        duration_seconds: Actual duration of session in seconds
    """

    id: int | None
    session_type: SessionType
    start_time: datetime
    end_time: datetime
    duration_seconds: int

    @property
    def duration_display(self) -> str:
        """Formatted duration for display.

        Returns:
            Duration in "X min" format (e.g., "25 min", "5 min")
        """
        minutes = self.duration_seconds // 60
        return f"{minutes} min"

    @property
    def date(self) -> datetime:
        """Date portion of start_time for grouping.

        Returns:
            Date object for the session start
        """
        return self.start_time.date()

    @property
    def time_range_display(self) -> str:
        """Formatted time range for display.

        Returns:
            Time range in "HH:MM - HH:MM" format
        """
        start_str = self.start_time.strftime("%H:%M")
        end_str = self.end_time.strftime("%H:%M")
        return f"{start_str} - {end_str}"

    @classmethod
    def from_session(cls, session: TimerSession) -> "CompletedSession":
        """Create CompletedSession from active session.

        Args:
            session: The TimerSession that completed

        Returns:
            New CompletedSession instance

        Raises:
            ValueError: If session is not in COMPLETED state or missing required data
        """
        if session.session_type is None:
            raise ValueError("Cannot create CompletedSession from session without type")
        if session.start_time is None:
            raise ValueError("Cannot create CompletedSession from session without start_time")

        # Calculate actual duration from timestamps
        start_dt = datetime.fromtimestamp(session.start_time)
        end_dt = datetime.now()
        duration = int((end_dt - start_dt).total_seconds())

        # Ensure duration is at least 1 second
        if duration <= 0:
            duration = 1

        return cls(
            id=None,  # Will be assigned by database
            session_type=session.session_type,
            start_time=start_dt,
            end_time=end_dt,
            duration_seconds=duration,
        )

    @classmethod
    def from_db_row(cls, row: sqlite3.Row) -> "CompletedSession":
        """Create CompletedSession from database row.

        Args:
            row: SQLite row from sessions table

        Returns:
            New CompletedSession instance
        """
        return cls(
            id=row["id"],
            session_type=SessionType[row["session_type"]],
            start_time=datetime.fromtimestamp(row["start_time"]),
            end_time=datetime.fromtimestamp(row["end_time"]),
            duration_seconds=row["duration_seconds"],
        )


# Configuration constants
DEFAULT_WORK_DURATION = 25
DEFAULT_SHORT_BREAK_DURATION = 5
DEFAULT_LONG_BREAK_DURATION = 15
MIN_DURATION = 1  # Minimum 1 minute
MAX_DURATION = 999  # Maximum 999 minutes


@dataclass
class TimerConfig:
    """User-configurable timer settings.

    Attributes:
        work_duration_minutes: Duration for work sessions (default: 25)
        short_break_minutes: Duration for short breaks (default: 5)
        long_break_minutes: Duration for long breaks (default: 15)
        theme: UI theme ("auto", "light", "dark", default: "auto")
    """

    # Class constants for validation
    DEFAULT_WORK_MINUTES = DEFAULT_WORK_DURATION
    DEFAULT_SHORT_BREAK_MINUTES = DEFAULT_SHORT_BREAK_DURATION
    DEFAULT_LONG_BREAK_MINUTES = DEFAULT_LONG_BREAK_DURATION
    MIN_DURATION = MIN_DURATION
    MAX_DURATION = MAX_DURATION

    work_duration_minutes: int = DEFAULT_WORK_DURATION
    short_break_minutes: int = DEFAULT_SHORT_BREAK_DURATION
    long_break_minutes: int = DEFAULT_LONG_BREAK_DURATION
    theme: str = "auto"

    def __post_init__(self) -> None:
        """Validate configuration values after initialization."""
        self._validate()

    def _validate(self) -> None:
        """Validate configuration values.

        Raises:
            ValueError: If any duration is out of valid range or theme is invalid
        """
        if not MIN_DURATION <= self.work_duration_minutes <= MAX_DURATION:
            raise ValueError(
                f"work_duration_minutes must be between {MIN_DURATION} and {MAX_DURATION}"
            )
        if not MIN_DURATION <= self.short_break_minutes <= MAX_DURATION:
            raise ValueError(
                f"short_break_minutes must be between {MIN_DURATION} and {MAX_DURATION}"
            )
        if not MIN_DURATION <= self.long_break_minutes <= MAX_DURATION:
            raise ValueError(
                f"long_break_minutes must be between {MIN_DURATION} and {MAX_DURATION}"
            )
        if self.theme not in ("auto", "light", "dark"):
            raise ValueError(f"theme must be 'auto', 'light', or 'dark', not '{self.theme}'")

    @classmethod
    def default(cls) -> "TimerConfig":
        """Create config with default values.

        Returns:
            New TimerConfig with default settings
        """
        return cls(
            work_duration_minutes=DEFAULT_WORK_DURATION,
            short_break_minutes=DEFAULT_SHORT_BREAK_DURATION,
            long_break_minutes=DEFAULT_LONG_BREAK_DURATION,
            theme="auto",
        )
