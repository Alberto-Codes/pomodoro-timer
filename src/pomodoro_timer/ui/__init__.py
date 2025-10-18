"""UI module for Pomodoro timer.

This module provides a web-based user interface using NiceGUI framework.
Users can view timer countdown, control sessions, view history, and configure settings.
"""

from pomodoro_timer.ui.app import run_ui

__all__ = ["AppState", "app_state", "run_ui"]


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
