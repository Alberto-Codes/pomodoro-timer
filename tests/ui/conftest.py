"""Test fixtures for UI acceptance tests.

This module provides shared fixtures for testing NiceGUI components.
The user fixture is automatically provided by the NiceGUI testing plugin.
"""

import pytest
from nicegui import ui

from pomodoro_timer.models.types import SessionState
from pomodoro_timer.ui.pages.main import main_page
from pomodoro_timer.ui.state import app_state


@pytest.fixture(scope="function", autouse=True)
def reset_app_state():
    """Reset app state before each test."""
    if app_state.session.state != SessionState.IDLE:
        app_state.cancel()
    yield
    # Clean up after test
    if app_state.session.state != SessionState.IDLE:
        app_state.cancel()


# Register the main page route for NiceGUI testing
ui.page("/")(main_page)
