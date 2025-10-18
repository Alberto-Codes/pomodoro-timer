"""UI module for Pomodoro timer.

This module provides a web-based user interface using NiceGUI framework.
Users can view timer countdown, control sessions, view history, and configure settings.
"""

from pomodoro_timer.ui.state import AppState, app_state

__all__ = ["AppState", "app_state", "run_ui"]


def run_ui() -> None:
    """Launch the NiceGUI web interface.
    
    Starts the web server and opens the UI in a browser.
    This function is called when running `pomodoro-timer --ui`.
    """
    # Will be implemented in Phase 3
    raise NotImplementedError("UI not yet implemented")
