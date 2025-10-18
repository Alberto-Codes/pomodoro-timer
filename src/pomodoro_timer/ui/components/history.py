"""Session history component.

This module provides the session_history() component that displays
completed Pomodoro sessions in a table format with pagination and clear functionality.
"""

from nicegui import ui

from pomodoro_timer.ui.state import app_state


def session_history() -> None:
    """Display session history table with completed sessions.

    Shows a table of completed sessions with columns:
    - Type (Work/Break)
    - Date (MM/DD/YYYY)
    - Time Range (HH:MM - HH:MM)
    - Duration (X min)

    Features:
    - Automatically updates when new sessions complete (via observable list)
    - Clear History button with confirmation
    - Responsive layout
    """
    with ui.card().classes("w-full max-w-4xl"):
        ui.label("Session History").classes("text-h6 mb-4")

        # History table
        with ui.column().classes("w-full"):
            if len(app_state.history) == 0:
                ui.label("No sessions completed yet").classes("text-gray-500 italic")
            else:
                # Table header
                with ui.row().classes("w-full font-bold border-b pb-2 mb-2"):
                    ui.label("Type").classes("flex-1")
                    ui.label("Date").classes("flex-1")
                    ui.label("Time Range").classes("flex-1")
                    ui.label("Duration").classes("flex-1")

                # Table rows - bind to observable history list
                for session in app_state.history:
                    with ui.row().classes("w-full py-2 border-b"):
                        # Type column
                        type_label = "Work" if session.session_type.name == "WORK" else "Break"
                        type_color = (
                            "text-blue-600"
                            if session.session_type.name == "WORK"
                            else "text-green-600"
                        )
                        ui.label(type_label).classes(f"flex-1 font-medium {type_color}")

                        # Date column
                        date_str = session.start_time.strftime("%m/%d/%Y")
                        ui.label(date_str).classes("flex-1")

                        # Time Range column
                        ui.label(session.time_range_display).classes("flex-1")

                        # Duration column
                        ui.label(session.duration_display).classes("flex-1")

        # Clear history button
        with ui.row().classes("w-full justify-end mt-4"):
            ui.button(
                "Clear History", on_click=lambda: _confirm_clear_history(), color="negative"
            ).props("outline")


def _confirm_clear_history() -> None:
    """Show confirmation dialog before clearing history."""
    with ui.dialog() as dialog, ui.card():
        ui.label("Are you sure you want to clear all history?")
        ui.label("This action cannot be undone.").classes("text-gray-500 text-sm")

        with ui.row().classes("w-full justify-end mt-4 gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button(
                "Clear All", on_click=lambda: _clear_history_confirmed(dialog), color="negative"
            )

    dialog.open()


def _clear_history_confirmed(dialog) -> None:
    """Clear history after confirmation."""
    app_state.clear_history()
    dialog.close()
    ui.notify("History cleared", type="positive")
