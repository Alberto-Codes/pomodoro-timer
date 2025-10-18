"""Timer display component for showing current timer state.

This component displays the current timer countdown, session type, progress, and state.
"""

from nicegui import ui

from pomodoro_timer.ui.state import AppState


@ui.refreshable
def timer_display(state: AppState) -> None:
    """Display current timer state.

    Args:
        state: Application state to observe and display

    UI Elements:
        - Large time display (formatted as MM:SS)
        - Session type label (Work/Break/Idle)
        - Progress bar (0-100%)
        - State indicator badge (Running/Paused/Idle)

    The display automatically refreshes via the @ui.refreshable decorator
    and is called every 1 second by a ui.timer in the main page.
    """
    with ui.column().classes("items-center gap-4 p-8"):
        # Session type and state badge
        with ui.row().classes("items-center gap-4"):
            ui.label(state.current_type_display).classes("text-2xl font-bold text-gray-700")

            # State badge with conditional styling
            if state.is_running:
                ui.badge("Running").props("color=green")
            elif state.is_paused:
                ui.badge("Paused").props("color=orange")
            elif state.is_idle:
                ui.badge("Idle").props("color=gray")

        # Large time display
        ui.label(state.current_time_display).classes("text-6xl font-mono font-bold text-blue-600")

        # Progress bar (only show if session active)
        if state.session.is_active:
            ui.linear_progress(value=state.progress_percentage / 100.0, show_value=True).props(
                "size=25px color=primary"
            )
            ui.label(f"{state.progress_percentage:.1f}% complete").classes("text-sm text-gray-500")
