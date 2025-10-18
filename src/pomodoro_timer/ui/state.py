"""Application state management for UI.

This module provides the central AppState class that bridges UI components
with the timer engine and manages observable state for reactive updates.
"""

from datetime import datetime

from nicegui import observables

from pomodoro_timer.models.session import TimerSession
from pomodoro_timer.models.types import SessionDurations, SessionState
from pomodoro_timer.timer.engine import TimerEngine
from pomodoro_timer.ui.config import ConfigManager
from pomodoro_timer.ui.database import SessionDatabase
from pomodoro_timer.ui.models import CompletedSession, TimerConfig


class AppState:
    """Central application state bridge between UI and timer engine.

    This class exposes observable properties that UI components can bind to
    for reactive updates, and provides control methods that delegate to the
    existing timer engine.
    """

    def __init__(self) -> None:
        """Initialize application state."""
        self._session = TimerSession()
        self._engine = TimerEngine(self._session)
        self._history: observables.ObservableList[CompletedSession] = observables.ObservableList()
        self._config = TimerConfig.default()
        self._database = SessionDatabase()
        self._config_manager = ConfigManager()

    # ===== Properties (Read-Only) =====

    @property
    def session(self) -> TimerSession:
        """Current timer session.

        Returns:
            The active TimerSession instance containing current state.
        """
        return self._session

    @property
    def engine(self) -> TimerEngine:
        """Timer engine instance.

        Returns:
            The TimerEngine managing the countdown loop.
        """
        return self._engine

    @property
    def history(self) -> observables.ObservableList[CompletedSession]:
        """Observable list of completed sessions.

        Returns:
            List that automatically notifies UI when sessions are added.
        """
        return self._history

    @property
    def config(self) -> TimerConfig:
        """Current timer configuration.

        Returns:
            The current TimerConfig with user settings.
        """
        return self._config

    # ===== Computed Properties (Read-Only) =====

    @property
    def progress_percentage(self) -> float:
        """Progress through current session as percentage.

        Returns:
            0.0 if idle, 0-100 if active session, based on time elapsed.

        Example:
            - Idle: 0.0
            - 5 min into 25 min work: 20.0
            - 24 min into 25 min work: 96.0
        """
        if self._session.state == SessionState.IDLE:
            return 0.0

        if self._session.session_type is None:
            return 0.0

        total_seconds = self._session.session_type.duration_seconds
        elapsed_seconds = total_seconds - self._session.remaining_seconds

        return (elapsed_seconds / total_seconds) * 100.0

    @property
    def is_idle(self) -> bool:
        """Check if no session is active.

        Returns:
            True if session.state == SessionState.IDLE
        """
        return self._session.state == SessionState.IDLE

    @property
    def is_running(self) -> bool:
        """Check if session is running.

        Returns:
            True if session.state == SessionState.RUNNING
        """
        return self._session.state == SessionState.RUNNING

    @property
    def is_paused(self) -> bool:
        """Check if session is paused.

        Returns:
            True if session.state == SessionState.PAUSED
        """
        return self._session.state == SessionState.PAUSED

    @property
    def current_time_display(self) -> str:
        """Formatted time for display.

        Returns:
            "MM:SS" format (e.g., "25:00", "04:37")
            "00:00" if idle.
        """
        return self._session.formatted_time

    @property
    def current_type_display(self) -> str:
        """Session type for display.

        Returns:
            "Work", "Break", or "Idle"
        """
        if self._session.session_type is None:
            return "Idle"
        return self._session.session_type.display_name

    # ===== Control Methods (Async) =====

    async def start_work(self) -> None:
        """Start a new work session.

        Raises:
            SessionAlreadyActive: If session already running or paused.

        Postconditions:
            - session.state == SessionState.RUNNING
            - session.session_type == SessionType.WORK
            - session.remaining_seconds == work_duration * 60
        """
        import asyncio

        # Start session state (validates not already active)
        self._session.start_work()
        # Set engine running flag and run countdown in background (non-blocking for UI)
        self._engine._running = True
        asyncio.create_task(self._engine._run_countdown())

    async def start_break(self) -> None:
        """Start a new break session.

        Raises:
            SessionAlreadyActive: If session already running or paused.

        Postconditions:
            - session.state == SessionState.RUNNING
            - session.session_type == SessionType.BREAK
            - session.remaining_seconds == break_duration * 60
        """
        import asyncio

        # Start session state (validates not already active)
        self._session.start_break()
        # Set engine running flag and run countdown in background (non-blocking for UI)
        self._engine._running = True
        asyncio.create_task(self._engine._run_countdown())

    def pause(self) -> None:
        """Pause the currently running session.

        Raises:
            InvalidStateTransition: If state is not RUNNING.

        Postconditions:
            - session.state == SessionState.PAUSED
            - session.remaining_seconds preserved
        """
        self._engine.pause()

    async def resume(self) -> None:
        """Resume a paused session.

        Raises:
            InvalidStateTransition: If state is not PAUSED.

        Postconditions:
            - session.state == SessionState.RUNNING
            - Countdown continues from paused time
        """
        import asyncio

        # Resume session state (validates currently paused)
        self._session.resume()
        # Set engine running flag and run countdown in background (non-blocking for UI)
        self._engine._running = True
        asyncio.create_task(self._engine._run_countdown())

    def cancel(self) -> None:
        """Cancel the current session and return to idle.

        Postconditions:
            - session.state == SessionState.IDLE
            - session.session_type == None
            - session.remaining_seconds == 0
        """
        self._engine.cancel()

    # ===== History Methods =====

    def check_and_record_completion(self) -> None:
        """Check if session completed and record it if so.

        This method should be called periodically (e.g., every second)
        to detect when a session transitions to COMPLETED state.
        Shows a notification when session completes.
        """
        from nicegui import ui

        if self._session.state == SessionState.COMPLETED and self._session.session_type:
            # Get session type before recording
            session_type = self._session.session_type.name.title()

            # Record the completion
            self.record_completion()

            # Show completion notification
            ui.notify(
                f"🎉 {session_type} session completed!",
                type="positive",
                position="top",
            )

            # Reset to idle for next session
            self._session.reset()

    def record_completion(self) -> None:
        """Save completed session to history and database.

        Preconditions:
            - session.state == SessionState.COMPLETED

        Postconditions:
            - Completed session added to database
            - Session appended to history observable list
            - UI automatically updates via observable
        """
        completed = CompletedSession.from_session(self._session)
        session_id = self._database.insert(completed)
        completed.id = session_id
        self._history.append(completed)

    def load_history(self, limit: int = 100, offset: int = 0) -> list[CompletedSession]:
        """Load session history from database.

        Args:
            limit: Maximum number of sessions to return (default: 100)
            offset: Number of sessions to skip (for pagination, default: 0)

        Returns:
            List of CompletedSession objects
        """
        return self._database.query_all(limit=limit, offset=offset)

    def get_history_by_date(self, date: datetime) -> list[CompletedSession]:
        """Filter sessions by date.

        Args:
            date: Date to filter sessions by

        Returns:
            List of sessions for the specified date
        """
        return self._database.query_by_date(date)

    def clear_history(self) -> None:
        """Delete all sessions from history.

        Postconditions:
            - All sessions deleted from database
            - History observable list cleared
        """
        self._database.delete_all()
        self._history.clear()

    # ===== Config Methods =====

    def load_config(self) -> TimerConfig:
        """Load configuration from TOML file.

        Returns:
            The loaded TimerConfig

        Postconditions:
            - Config loaded from file (or default if file doesn't exist)
            - Config applied to SessionType durations
        """
        self._config = self._config_manager.load()
        self.apply_config(self._config)
        return self._config

    def save_config(self, config: TimerConfig) -> None:
        """Validate and save configuration.

        Args:
            config: The TimerConfig to save

        Raises:
            ValueError: If config validation fails

        Postconditions:
            - Config validated and saved to file
            - Config applied to SessionType durations
        """
        self._config_manager.save(config)
        self._config = config
        self.apply_config(config)

    def apply_config(self, config: TimerConfig) -> None:
        """Apply configuration to SessionType durations.

        Args:
            config: The TimerConfig to apply

        Note:
            This modifies the SessionDurations class attributes.
        """
        # Update SessionDurations from config
        SessionDurations.work_duration_seconds = config.work_duration_minutes * 60
        SessionDurations.break_duration_seconds = config.short_break_minutes * 60

    def reset_config(self) -> None:
        """Reset configuration to defaults.

        Postconditions:
            - Config reset to defaults and saved to file
            - Config applied to SessionType durations
        """
        self._config_manager.reset_to_defaults()
        self._config = TimerConfig.default()
        self.apply_config(self._config)


# Global app state instance
app_state = AppState()
