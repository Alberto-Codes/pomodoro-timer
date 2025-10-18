"""Main UI application module.

This module provides the NiceGUI application entry point.
"""

from nicegui import app, ui

from pomodoro_timer.ui.state import app_state


def run_ui(*, reload: bool = False, port: int = 8080) -> None:
    """Launch the NiceGUI web interface.
    
    Args:
        reload: Enable auto-reload for development (default: False)
        port: Port number to run server on (default: 8080)
    
    This function starts the web server and opens the UI in a browser.
    Called when running `pomodoro-timer --ui`.
    """
    # Reset timer to idle on app start
    if app_state.session.state != "idle":
        app_state.cancel()
    
    # Register routes
    @ui.page("/")
    def main_page():
        """Main page with timer display and controls.
        
        This is a stub implementation that will be replaced
        with actual components in Phase 3.
        """
        ui.label("Pomodoro Timer UI - Not Yet Implemented")
        ui.label("Timer display and controls coming soon...")
    
    # Run the app
    ui.run(port=port, reload=reload, title="Pomodoro Timer")
