"""Main page layout for Pomodoro Timer UI.

This module provides the main page that combines timer display and control components.
"""

from nicegui import ui

from pomodoro_timer.ui.components.controls import control_buttons
from pomodoro_timer.ui.components.history import session_history
from pomodoro_timer.ui.components.settings import open_settings_dialog
from pomodoro_timer.ui.components.timer_display import timer_display
from pomodoro_timer.ui.state import app_state


def main_content() -> None:
    """Render main page content with timer display and controls.

    This function sets up:
    - Timer display (refreshable, updates every second)
    - Control buttons (conditional based on state)
    - Session history view
    - Automatic refresh timer (1-second interval)
    """
    # Header with settings button
    with ui.header().classes("items-center justify-between px-8"):
        ui.label("🍅 Pomodoro Timer").classes("text-2xl font-bold")
        ui.button("Settings", on_click=open_settings_dialog).props("flat icon=settings")

    # Main content area
    with ui.column().classes("items-center justify-center flex-grow gap-8 p-8"):
        # Timer display (refreshable)
        timer_display(app_state)

        # Control buttons
        with ui.card().classes("p-6"):
            control_buttons(app_state)

        # Session history
        session_history()

    # Auto-refresh timer display every 1 second
    ui.timer(1.0, lambda: timer_display.refresh())

    # Check for session completion every second
    ui.timer(1.0, lambda: app_state.check_and_record_completion())


def main_page() -> None:
    """Main page route handler.

    This is the entry point for the UI, called when users navigate to '/'.
    It sets up the page structure and initializes the timer display.
    """
    # Page configuration
    ui.colors(primary="#3B82F6", secondary="#10B981", accent="#F59E0B")

    # Render main content
    main_content()
