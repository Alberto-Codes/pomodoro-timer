"""Control buttons component for timer actions.

This component provides buttons to start, pause, resume, and cancel timer sessions.
"""

from nicegui import ui

from pomodoro_timer.models.exceptions import InvalidStateTransition, SessionAlreadyActive
from pomodoro_timer.ui.state import AppState


@ui.refreshable
def control_buttons(state: AppState) -> None:
    """Display timer control buttons.

    Args:
        state: Application state to control

    Buttons displayed conditionally based on current state:
        - Start Work / Start Break: Visible when idle
        - Pause: Visible when running
        - Resume: Visible when paused
        - Cancel: Visible when running or paused

    All buttons include error handling with user-friendly notifications.
    """

    async def handle_start_work():
        """Handle Start Work button click."""
        try:
            await state.start_work()
            ui.notify("Work session started!", type="positive")
        except SessionAlreadyActive:
            ui.notify("A session is already active", type="warning")
        except Exception as e:
            ui.notify(f"Error starting work session: {e}", type="negative")

    async def handle_start_break():
        """Handle Start Break button click."""
        try:
            await state.start_break()
            ui.notify("Break session started!", type="positive")
        except SessionAlreadyActive:
            ui.notify("A session is already active", type="warning")
        except Exception as e:
            ui.notify(f"Error starting break session: {e}", type="negative")

    def handle_pause():
        """Handle Pause button click."""
        try:
            state.pause()
            ui.notify("Session paused", type="info")
        except InvalidStateTransition:
            ui.notify("Cannot pause - session not running", type="warning")
        except Exception as e:
            ui.notify(f"Error pausing session: {e}", type="negative")

    async def handle_resume():
        """Handle Resume button click."""
        try:
            await state.resume()
            ui.notify("Session resumed", type="positive")
        except InvalidStateTransition:
            ui.notify("Cannot resume - session not paused", type="warning")
        except Exception as e:
            ui.notify(f"Error resuming session: {e}", type="negative")

    def handle_cancel():
        """Handle Cancel button click."""
        try:
            state.cancel()
            ui.notify("Session cancelled", type="info")
        except Exception as e:
            ui.notify(f"Error cancelling session: {e}", type="negative")

    # Button layout
    with ui.row().classes("gap-4 justify-center"):
        # Start buttons (visible when idle)
        if state.is_idle:
            ui.button("Start Work", on_click=handle_start_work, icon="work").props(
                "color=primary size=lg"
            )

            ui.button("Start Break", on_click=handle_start_break, icon="coffee").props(
                "color=secondary size=lg"
            )

        # Pause button (visible when running)
        elif state.is_running:
            ui.button("Pause", on_click=handle_pause, icon="pause").props("color=orange size=lg")

            ui.button("Cancel", on_click=handle_cancel, icon="stop").props("color=red size=lg")

        # Resume button (visible when paused)
        elif state.is_paused:
            ui.button("Resume", on_click=handle_resume, icon="play_arrow").props(
                "color=green size=lg"
            )

            ui.button("Cancel", on_click=handle_cancel, icon="stop").props("color=red size=lg")
