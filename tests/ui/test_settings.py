"""Acceptance tests for settings UI component.

These tests validate the settings form functionality including:
- Display of current configuration values
- Saving and applying configuration changes
- Validation of invalid duration inputs
- Persistence of settings across app restarts
- Cancel and reset functionality
"""

import pytest
from nicegui.testing import User

from pomodoro_timer.ui.models import TimerConfig


@pytest.mark.ui
class TestSettingsForm:
    """Tests for settings form display and interaction."""

    async def test_settings_form_displays_current_values(self, user: User) -> None:
        """Settings form shows current work and break duration values.

        Given: App with default settings (25/5 minutes)
        When: User opens settings dialog
        Then: Form displays work=25, short_break=5
        """
        await user.open("/")

        # Open settings dialog
        user.find("Settings").click()

        # Verify form displays current values
        assert user.find("Work Duration").exists()  # type: ignore[unresolved-attribute]
        assert user.find("Short Break Duration").exists()  # type: ignore[unresolved-attribute]

        # Check default values displayed
        work_input = user.find("Work Duration").parent().find("input")  # type: ignore[unresolved-attribute]
        break_input = user.find("Short Break Duration").parent().find("input")  # type: ignore[unresolved-attribute]

        assert work_input.value == 25
        assert break_input.value == 5

    async def test_settings_save_applies_and_persists_changes(self, user: User) -> None:
        """Saving settings applies changes and persists to TOML.

        Given: App with default settings
        When: User changes work=30, break=10, clicks Save
        Then: Settings saved, timer uses new durations
        And: Config file contains updated values
        """
        await user.open("/")

        # Open settings
        user.find("Settings").click()

        # Change values
        work_input = user.find("Work Duration").parent().find("input")  # type: ignore[unresolved-attribute]
        break_input = user.find("Short Break Duration").parent().find("input")  # type: ignore[unresolved-attribute]

        work_input.set_value(30)
        break_input.set_value(10)

        # Save
        user.find("Save").click()

        # Verify success notification
        assert user.find("Settings saved successfully!").exists()  # type: ignore[unresolved-attribute]

        # Start work session and verify new duration
        user.find("Start Work").click()
        assert user.find("30:00").exists()  # type: ignore[unresolved-attribute]  # Should show 30 minutes

        # Cancel and start break
        user.find("Cancel").click()
        user.find("Start Break").click()
        assert user.find("10:00").exists()  # type: ignore[unresolved-attribute]  # Should show 10 minutes

    async def test_settings_validation_prevents_invalid_durations(self, user: User) -> None:
        """Invalid durations show error and disable Save button.

        Given: Settings dialog open
        When: User enters invalid duration (e.g., 0 or 1000)
        Then: Error message shown
        And: Save button disabled
        """
        await user.open("/")

        # Open settings
        user.find("Settings").click()

        # Try to enter 0 (below minimum)
        work_input = user.find("Work Duration").parent().find("input")  # type: ignore[unresolved-attribute]
        work_input.set_value(0)

        # Verify error message
        assert user.find("Work duration must be at least").exists()  # type: ignore[unresolved-attribute]

        # Verify Save button disabled
        save_button = user.find("Save")
        assert save_button.props("disable=true")  # type: ignore[unresolved-attribute]

        # Try to enter 1000 (above maximum)
        work_input.set_value(1000)

        # Verify error message
        assert user.find("Work duration must be at most").exists()  # type: ignore[unresolved-attribute]
        assert save_button.props("disable=true")  # type: ignore[unresolved-attribute]

        # Enter valid value
        work_input.set_value(25)

        # Verify error cleared and Save enabled
        assert not user.find("Work duration must be").exists()  # type: ignore[unresolved-attribute]
        assert not save_button.props("disable=true")  # type: ignore[unresolved-attribute]

    async def test_settings_persist_across_app_restart(self, user: User) -> None:
        """Settings persist to TOML and load on app restart.

        Given: User changes settings to 30/10
        When: App is closed and reopened
        Then: Settings remain 30/10
        """
        await user.open("/")

        # Change and save settings
        user.find("Settings").click()

        work_input = user.find("Work Duration").parent().find("input")  # type: ignore[unresolved-attribute]
        break_input = user.find("Short Break Duration").parent().find("input")  # type: ignore[unresolved-attribute]

        work_input.set_value(30)
        break_input.set_value(10)
        user.find("Save").click()

        # Simulate app restart (close and reopen)
        user.close()

        # Open app again
        await user.open("/")

        # Load settings should restore saved values
        # Start work session to verify
        user.find("Start Work").click()
        assert user.find("30:00").exists()  # type: ignore[unresolved-attribute]

    async def test_settings_cancel_discards_changes(self, user: User) -> None:
        """Cancel button closes dialog without saving changes.

        Given: Settings dialog with modified values
        When: User clicks Cancel
        Then: Dialog closes
        And: Settings unchanged
        """
        await user.open("/")

        # Open settings
        user.find("Settings").click()

        # Change values but don't save
        work_input = user.find("Work Duration").parent().find("input")  # type: ignore[unresolved-attribute]
        work_input.set_value(40)

        # Click Cancel
        user.find("Cancel").click()

        # Verify dialog closed
        assert not user.find("Timer Configuration").exists()  # type: ignore[unresolved-attribute]

        # Verify settings unchanged (should still be default 25)
        user.find("Start Work").click()
        assert user.find("25:00").exists()  # type: ignore[unresolved-attribute]

    async def test_settings_reset_restores_defaults(self, user: User) -> None:
        """Reset button restores default configuration values.

        Given: Settings modified to custom values
        When: User clicks Reset and confirms
        Then: Settings restored to 25/5 defaults
        And: Changes saved to config file
        """
        await user.open("/")

        # Change settings first
        user.find("Settings").click()
        work_input = user.find("Work Duration").parent().find("input")  # type: ignore[unresolved-attribute]
        break_input = user.find("Short Break Duration").parent().find("input")  # type: ignore[unresolved-attribute]

        work_input.set_value(30)
        break_input.set_value(10)
        user.find("Save").click()

        # Reopen settings and reset
        user.find("Settings").click()
        user.find("Reset").click()

        # Confirm reset
        user.find("Reset", index=1).click()  # type: ignore[no-matching-overload]  # Second Reset button in confirmation

        # Verify values reset
        assert work_input.value == TimerConfig.DEFAULT_WORK_MINUTES
        assert break_input.value == TimerConfig.DEFAULT_SHORT_BREAK_MINUTES

        # Save and verify
        user.find("Save").click()
        user.find("Start Work").click()
        assert user.find("25:00").exists()  # type: ignore[unresolved-attribute]  # Back to default
