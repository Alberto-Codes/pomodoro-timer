"""Root conftest for pytest configuration."""

from pathlib import Path

import pytest

# Enable NiceGUI testing plugin
pytest_plugins = ["nicegui.testing.user_plugin"]


def pytest_configure(config):
    """Configure pytest with NiceGUI settings."""
    # Set the main_file configuration for NiceGUI testing
    # This points to the entry point of our NiceGUI app
    config._inicache["main_file"] = str(
        Path(__file__).parent / "src" / "pomodoro_timer" / "ui" / "app.py"
    )


@pytest.fixture(autouse=True)
def reset_session_durations():
    """Reset SessionDurations to defaults before each test."""
    from pomodoro_timer.models.types import SessionDurations

    # Save original
    original_work = SessionDurations.work_duration_seconds
    original_break = SessionDurations.break_duration_seconds

    # Reset to defaults
    SessionDurations.work_duration_seconds = 1500
    SessionDurations.break_duration_seconds = 300

    yield

    # Restore (for safety, though we reset at start)
    SessionDurations.work_duration_seconds = original_work
    SessionDurations.break_duration_seconds = original_break
