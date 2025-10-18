"""Main UI application module.

This module provides the NiceGUI application entry point.
"""

from nicegui import ui

from pomodoro_timer.models.types import SessionState
from pomodoro_timer.ui.keyboard import setup_keyboard_shortcuts
from pomodoro_timer.ui.pages.main import main_page
from pomodoro_timer.ui.state import app_state


def run_ui(*, reload: bool = False, port: int = 8080) -> None:
    """Launch the NiceGUI web interface.

    Args:
        reload: Enable auto-reload for development (default: False)
        port: Port number to run server on (default: 8080)

    This function starts the web server and opens the UI in a browser.
    Called when running `pomodoro-timer --ui`.

    The timer is automatically reset to idle state on app startup to ensure
    a clean state (no sessions persist across app restarts per edge case requirement).
    """
    # Reset timer to idle on app start (edge case: app closed while timer running)
    if app_state.session.state != SessionState.IDLE:
        app_state.cancel()

    # Load user configuration
    app_state.load_config()

    # Setup global keyboard shortcuts
    setup_keyboard_shortcuts(app_state)

    # Register main page route
    ui.page("/")(main_page)

    # Run the app
    ui.run(port=port, reload=reload, title="🍅 Pomodoro Timer")
