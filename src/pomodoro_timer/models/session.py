"""TimerSession class for managing Pomodoro timer state."""

import time

from pomodoro_timer.models.exceptions import InvalidStateTransition, SessionAlreadyActive
from pomodoro_timer.models.types import SessionState, SessionType


class TimerSession:
    """Represents a Pomodoro timer session with state management."""

    def __init__(self) -> None:
        """Initialize a new timer session in IDLE state."""
        self.state: SessionState = SessionState.IDLE
        self.session_type: SessionType | None = None
        self.remaining_seconds: int = 0
        self.start_time: float | None = None
        self.end_time: float | None = None

    @property
    def is_active(self) -> bool:
        """Check if session is running or paused.

        Returns:
            True if state is RUNNING or PAUSED, False otherwise
        """
        return self.state in (SessionState.RUNNING, SessionState.PAUSED)

    @property
    def formatted_time(self) -> str:
        """Get remaining time formatted as MM:SS.

        Returns:
            Time string in MM:SS format with zero-padding
        """
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def start_work(self) -> None:
        """Start a new 25-minute work session.

        Raises:
            SessionAlreadyActive: If session already running or paused
        """
        if self.state in (SessionState.RUNNING, SessionState.PAUSED):
            raise SessionAlreadyActive("Cannot start new session while one is already active")

        self.session_type = SessionType.WORK
        self.state = SessionState.RUNNING
        self.remaining_seconds = SessionType.WORK.duration_seconds
        self.start_time = time.time()
        self.end_time = self.start_time + self.remaining_seconds

    def start_break(self) -> None:
        """Start a new 5-minute break session.

        Raises:
            SessionAlreadyActive: If session already running or paused
        """
        if self.state in (SessionState.RUNNING, SessionState.PAUSED):
            raise SessionAlreadyActive("Cannot start new session while one is already active")

        self.session_type = SessionType.BREAK
        self.state = SessionState.RUNNING
        self.remaining_seconds = SessionType.BREAK.duration_seconds
        self.start_time = time.time()
        self.end_time = self.start_time + self.remaining_seconds

    def pause(self) -> None:
        """Pause the currently running session.

        Raises:
            InvalidStateTransition: If state is not RUNNING
        """
        if self.state != SessionState.RUNNING:
            raise InvalidStateTransition(f"Cannot pause from {self.state.value} state")

        # Calculate and preserve remaining time
        if self.end_time is not None:
            self.remaining_seconds = max(0, int(self.end_time - time.time()))

        self.state = SessionState.PAUSED
        self.end_time = None  # Clear end_time, keep start_time for resume

    def resume(self) -> None:
        """Resume a paused session.

        Raises:
            InvalidStateTransition: If state is not PAUSED
        """
        if self.state != SessionState.PAUSED:
            raise InvalidStateTransition(f"Cannot resume from {self.state.value} state")

        self.state = SessionState.RUNNING
        # Recalculate end_time based on remaining seconds
        self.end_time = time.time() + self.remaining_seconds

    def cancel(self) -> None:
        """Cancel the current session and return to idle.

        Can be called from RUNNING, PAUSED, or COMPLETED states.
        """
        self.state = SessionState.IDLE
        self.session_type = None
        self.remaining_seconds = 0
        self.start_time = None
        self.end_time = None

    def tick(self) -> None:
        """Update remaining time based on current time.

        Should be called periodically (e.g., every 0.1s) when state is RUNNING.
        Automatically transitions to COMPLETED when time reaches zero.
        """
        if self.state != SessionState.RUNNING:
            return

        if self.end_time is None:
            return

        # Calculate remaining time
        remaining = self.end_time - time.time()

        if remaining <= 0:
            # Session completed
            self.remaining_seconds = 0
            self.state = SessionState.COMPLETED
            self.start_time = None
            self.end_time = None
        else:
            # Update remaining seconds
            self.remaining_seconds = int(remaining)
