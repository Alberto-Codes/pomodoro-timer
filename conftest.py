"""Root conftest for pytest configuration."""

from pathlib import Path

# Enable NiceGUI testing plugin
pytest_plugins = ["nicegui.testing.user_plugin"]


def pytest_configure(config):
    """Configure pytest with NiceGUI settings."""
    # Set the main_file configuration for NiceGUI testing
    # This points to the entry point of our NiceGUI app
    config._inicache["main_file"] = str(
        Path(__file__).parent / "src" / "pomodoro_timer" / "ui" / "app.py"
    )
