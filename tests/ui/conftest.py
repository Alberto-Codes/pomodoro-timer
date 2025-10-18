"""Test fixtures for UI acceptance tests.

This module provides shared fixtures for testing NiceGUI components.
The user fixture is automatically provided by the NiceGUI testing plugin.
"""

import pytest


# Configure NiceGUI testing to use our app
@pytest.fixture(scope="session", autouse=True)
def nicegui_config():
    """Configure NiceGUI testing."""
    from nicegui import app
    # Import to ensure app routes are registered
    import pomodoro_timer.ui.app  # noqa: F401
