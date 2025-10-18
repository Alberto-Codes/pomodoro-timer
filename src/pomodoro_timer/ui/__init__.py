"""UI module for Pomodoro timer.

This module provides a web-based user interface using NiceGUI framework.
Users can view timer countdown, control sessions, view history, and configure settings.
"""

__all__ = ["AppState", "app_state", "run_ui"]


def run_ui() -> None:
    """Launch the NiceGUI web interface.
    
    Starts the web server and opens the UI in a browser.
    This function is called when running `pomodoro-timer --ui`.
    """
    # Will be implemented in Phase 3
    raise NotImplementedError("UI not yet implemented")


# Delayed import to avoid circular dependency
def __getattr__(name: str):
    """Lazy import for AppState and app_state."""
    if name == "AppState":
        from pomodoro_timer.ui.state import AppState
        return AppState
    elif name == "app_state":
        from pomodoro_timer.ui.state import app_state
        return app_state
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
