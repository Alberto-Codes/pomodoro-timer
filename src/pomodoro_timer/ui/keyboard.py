"""Keyboard shortcuts for Pomodoro Timer UI.

This module provides global keyboard shortcut handlers that enable
quick access to timer controls without clicking buttons.
"""

from nicegui import ui

from pomodoro_timer.ui.state import AppState


def setup_keyboard_shortcuts(app_state: AppState) -> None:
    """Register global keyboard shortcuts for timer control.

    Shortcuts (FR-015 requirement):
    - Space: Start/Pause/Resume timer (context-sensitive)
    - Escape: Cancel current session and return to idle
    - W: Start work session (when idle)
    - B: Start break session (when idle)

    Args:
        app_state: The AppState instance to control

    Note:
        Shortcuts are registered globally and work on any page.
    """

    async def handle_space() -> None:
        """Handle Space key - context-sensitive start/pause/resume."""
        if app_state.is_idle:
            # Start work session from idle
            await app_state.start_work()
            ui.notify("Work session started (Space)", type="info")
        elif app_state.is_running:
            # Pause from running
            app_state.pause()
            ui.notify("Timer paused (Space)", type="info")
        elif app_state.is_paused:
            # Resume from paused
            await app_state.resume()
            ui.notify("Timer resumed (Space)", type="info")

    def handle_escape() -> None:
        """Handle Escape key - cancel current session."""
        if not app_state.is_idle:
            app_state.cancel()
            ui.notify("Session cancelled (Escape)", type="warning")

    async def handle_w() -> None:
        """Handle W key - start work session (when idle)."""
        if app_state.is_idle:
            await app_state.start_work()
            ui.notify("Work session started (W)", type="positive")

    async def handle_b() -> None:
        """Handle B key - start break session (when idle)."""
        if app_state.is_idle:
            await app_state.start_break()
            ui.notify("Break session started (B)", type="positive")

    # Register keyboard handlers
    ui.keyboard(on_key=lambda e: handle_space() if e.key == " " and not e.action.repeat else None)
    ui.keyboard(on_key=lambda e: handle_escape() if e.key == "Escape" else None)
    ui.keyboard(on_key=lambda e: handle_w() if str(e.key).lower() == "w" else None)
    ui.keyboard(on_key=lambda e: handle_b() if str(e.key).lower() == "b" else None)
