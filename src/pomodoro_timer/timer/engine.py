"""Timer engine for managing countdown loop."""

import asyncio

from pomodoro_timer.cli.display import clear_line, display_timer
from pomodoro_timer.models.session import TimerSession
from pomodoro_timer.models.types import SessionState
from pomodoro_timer.timer.notifications import notify_completion


class TimerEngine:
    """Manages the timer countdown loop and display updates."""

    def __init__(self, session: TimerSession) -> None:
        """Initialize timer engine with a session.

        Args:
            session: The timer session to manage
        """
        self.session = session
        self._running = False

    async def start_work(self) -> None:
        """Start a new 25-minute work session.

        Raises:
            SessionAlreadyActive: If session already running or paused
        """
        self.session.start_work()
        await self._run_countdown()

    async def start_break(self) -> None:
        """Start a new 5-minute break session.

        Raises:
            SessionAlreadyActive: If session already running or paused
        """
        self.session.start_break()
        await self._run_countdown()

    def pause(self) -> None:
        """Pause the currently running session."""
        self.session.pause()
        self._running = False

    async def resume(self) -> None:
        """Resume a paused session."""
        self.session.resume()
        await self._run_countdown()

    def cancel(self) -> None:
        """Cancel the current session."""
        self.session.cancel()
        self._running = False
        clear_line()

    async def _run_countdown(self) -> None:
        """Run the countdown loop with 10Hz refresh rate."""
        self._running = True

        try:
            while self._running and self.session.state == SessionState.RUNNING:
                # Update session time
                self.session.tick()

                # Check if completed
                if self.session.state == SessionState.COMPLETED:
                    clear_line()
                    if self.session.session_type:
                        notify_completion(self.session.session_type)
                    break

                # Display current time
                if self.session.session_type:
                    display_timer(
                        self.session.session_type.display_name,
                        self.session.formatted_time,
                        self.session.state.display_name,
                    )

                # Sleep for 0.1 seconds (10Hz refresh rate)
                await asyncio.sleep(0.1)

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            clear_line()
            print("\nTimer interrupted.")
            self.session.cancel()
            raise
