"""Settings form component for timer configuration.

This module provides the settings_form() UI component that allows users to
customize timer durations through a modal dialog interface.
"""

from nicegui import ui

from pomodoro_timer.ui.models import TimerConfig
from pomodoro_timer.ui.state import app_state


def settings_form() -> None:
    """Render settings form with duration inputs and validation.

    Displays:
    - Work duration input (1-999 minutes)
    - Short break duration input (1-999 minutes)
    - Long break duration (read-only, informational)
    - Save/Cancel/Reset buttons

    Form includes real-time validation with error messages and disabled Save
    button when values are invalid.
    """
    # Load current config
    config = app_state.config

    # State for form inputs
    work_duration = config.work_duration_minutes
    break_duration = config.short_break_minutes

    # Validation state
    work_error = ""
    break_error = ""

    def validate_duration(value: int, name: str) -> str:
        """Validate duration is in valid range (1-999)."""
        if value < TimerConfig.MIN_DURATION:
            return f"{name} must be at least {TimerConfig.MIN_DURATION} minute"
        if value > TimerConfig.MAX_DURATION:
            return f"{name} must be at most {TimerConfig.MAX_DURATION} minutes"
        return ""

    def is_form_valid() -> bool:
        """Check if all form inputs are valid."""
        nonlocal work_error, break_error
        work_error = validate_duration(work_input.value, "Work duration")
        break_error = validate_duration(break_input.value, "Short break duration")

        # Update error displays
        work_error_label.set_text(work_error)
        break_error_label.set_text(break_error)

        # Update save button state
        save_button.props(f"disable={bool(work_error or break_error)}")

        return not (work_error or break_error)

    async def save_settings():
        """Save settings and apply to timer."""
        if not is_form_valid():
            return

        try:
            # Create new config with updated values
            new_config = TimerConfig(
                work_duration_minutes=work_input.value,
                short_break_minutes=break_input.value,
                long_break_minutes=config.long_break_minutes,
                theme=config.theme,
            )

            # Save and apply
            app_state.save_config(new_config)

            ui.notify("Settings saved successfully!", type="positive")
            assert dialog is not None
            dialog.close()
        except ValueError as e:
            ui.notify(f"Error saving settings: {e}", type="negative")

    def cancel_settings():
        """Close dialog without saving."""
        assert dialog is not None
        dialog.close()

    async def reset_settings():
        """Reset settings to defaults."""
        # Confirm with user
        if await confirm_reset():
            try:
                app_state.reset_config()

                # Update form inputs
                work_input.value = TimerConfig.DEFAULT_WORK_MINUTES
                break_input.value = TimerConfig.DEFAULT_SHORT_BREAK_MINUTES

                # Revalidate
                is_form_valid()

                ui.notify("Settings reset to defaults", type="info")
            except Exception as e:
                ui.notify(f"Error resetting settings: {e}", type="negative")

    async def confirm_reset() -> bool:
        """Show confirmation dialog for reset action."""
        with ui.dialog().props("persistent") as reset_dialog, ui.card():
            ui.label("Reset settings to defaults?")
            with ui.row():
                ui.button("Cancel", on_click=lambda: reset_dialog.submit(False))
                ui.button("Reset", on_click=lambda: reset_dialog.submit(True)).props(
                    "color=negative"
                )

        result = await reset_dialog
        return result

    # Build form UI
    with ui.card().classes("w-full"):
        ui.label("Timer Configuration").classes("text-h6")

        ui.label("Customize timer durations for work sessions and breaks.")

        ui.separator()

        # Work duration input
        with ui.column().classes("w-full"):
            ui.label("Work Duration (minutes)")
            work_input = (
                ui.number(
                    value=work_duration,
                    min=TimerConfig.MIN_DURATION,
                    max=TimerConfig.MAX_DURATION,
                    step=1,
                    on_change=lambda: is_form_valid(),
                )
                .props("outlined dense")
                .classes("w-full")
            )
            work_error_label = ui.label("").classes("text-negative text-caption")

        # Short break duration input
        with ui.column().classes("w-full"):
            ui.label("Short Break Duration (minutes)")
            break_input = (
                ui.number(
                    value=break_duration,
                    min=TimerConfig.MIN_DURATION,
                    max=TimerConfig.MAX_DURATION,
                    step=1,
                    on_change=lambda: is_form_valid(),
                )
                .props("outlined dense")
                .classes("w-full")
            )
            break_error_label = ui.label("").classes("text-negative text-caption")

        # Long break info (read-only)
        with ui.column().classes("w-full"):
            ui.label("Long Break Duration")
            ui.label(f"{config.long_break_minutes} minutes (standard Pomodoro technique)").classes(
                "text-caption text-grey"
            )

        ui.separator()

        # Action buttons
        with ui.row().classes("w-full justify-end"):
            ui.button("Reset", on_click=reset_settings).props("outline")
            ui.button("Cancel", on_click=cancel_settings).props("outline")
            save_button = ui.button("Save", on_click=save_settings).props("color=primary")

        # Initial validation
        is_form_valid()


# Module-level dialog reference for opening from main page
dialog: ui.dialog | None = None


def open_settings_dialog():
    """Open settings dialog modal."""
    global dialog

    dialog = ui.dialog().props("persistent")

    with dialog, ui.card().classes("w-96"):
        settings_form()

    dialog.open()
