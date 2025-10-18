"""UI module for Pomodoro timer.

This module provides a web-based user interface using NiceGUI framework.
Users can view timer countdown, control sessions, view history, and configure settings.
"""

from pomodoro_timer.ui.app import run_ui
from pomodoro_timer.ui.state import AppState, app_state

__all__ = ["AppState", "app_state", "run_ui"]
