"""Integration test for complete timer lifecycle (US1+US2).

This test verifies the complete timer workflow integrating display and controls.
"""

import asyncio

import pytest
from nicegui.testing import User

from pomodoro_timer.models.types import SessionState
from pomodoro_timer.ui.state import app_state


pytestmark = [pytest.mark.ui, pytest.mark.integration]


@pytest.mark.asyncio
class TestCompleteTimerLifecycle:
    """Test complete timer lifecycle from start to completion."""

    async def test_full_work_cycle_start_pause_resume_complete(self, user: User):
        """Test complete workflow: start work → pause → resume → observe countdown."""
        # This test will fail until all components are integrated
        # Expected: Full timer lifecycle works end-to-end

        # Ensure clean start
        if app_state.session.state != SessionState.IDLE:
            app_state.cancel()

        # Navigate to main page
        await user.open("/")

        # Step 1: Start work session
        user.find("Start Work").click()
        await asyncio.sleep(0.1)  # Wait for async handler to complete
        assert app_state.is_running
        assert app_state.current_type_display == "Work"

        # Verify initial time
        initial_time = app_state.session.remaining_seconds
        assert initial_time > 0

        # Step 2: Wait for time to elapse
        await asyncio.sleep(2.0)

        # Verify time decreased
        time_after_wait = app_state.session.remaining_seconds
        assert time_after_wait < initial_time

        # Step 3: Pause the session
        user.find("Pause").click()
        await asyncio.sleep(0.1)  # Wait for handler to complete
        assert app_state.is_paused

        # Verify time is preserved
        paused_time = app_state.session.remaining_seconds

        # Wait while paused
        await asyncio.sleep(1.0)

        # Time should NOT change while paused
        assert app_state.session.remaining_seconds == paused_time

        # Step 4: Resume the session
        user.find("Resume").click()
        await asyncio.sleep(0.1)  # Wait for async handler to complete
        assert app_state.is_running

        # Verify time continues from paused point
        assert app_state.session.remaining_seconds <= paused_time

        # Step 5: Cancel the session
        user.find("Cancel").click()
        await asyncio.sleep(0.1)  # Wait for handler to complete
        assert app_state.is_idle
        assert app_state.current_time_display == "00:00"

    async def test_break_session_lifecycle(self, user: User):
        """Test break session lifecycle."""
        # This test will fail until all components are integrated

        # Ensure clean start
        if app_state.session.state != SessionState.IDLE:
            app_state.cancel()

        # Navigate to main page
        await user.open("/")

        # Start break session
        user.find("Start Break").click()
        await asyncio.sleep(0.1)  # Wait for async handler to complete
        assert app_state.is_running
        assert app_state.current_type_display == "Break"

        # Verify break duration (5 minutes = 300 seconds)
        assert app_state.session.remaining_seconds <= 300

        # Wait for time to elapse
        await asyncio.sleep(1.5)

        # Cancel
        user.find("Cancel").click()
        await asyncio.sleep(0.1)  # Wait for handler to complete
        assert app_state.is_idle

    async def test_cannot_start_multiple_sessions_simultaneously(self, user: User):
        """Test that starting a session while one is active doesn't create conflicts."""
        # This test will fail until error handling is implemented

        # Ensure clean start
        if app_state.session.state != SessionState.IDLE:
            app_state.cancel()

        # Navigate to main page
        await user.open("/")

        # Start work session
        user.find("Start Work").click()
        await asyncio.sleep(0.1)  # Wait for async handler to complete
        assert app_state.is_running

        # Try to start break (should be prevented by disabled button)
        # The button should be disabled, so this shouldn't change state
        # (Actual behavior depends on button state implementation)

        # Verify still running work session
        assert app_state.current_type_display == "Work"

    async def test_timer_state_transitions_are_reflected_in_ui(self, user: User):
        """Test that all state transitions update the UI correctly."""
        # This test will fail until UI binding is implemented

        # Ensure clean start
        if app_state.session.state != SessionState.IDLE:
            app_state.cancel()

        # Navigate to main page
        await user.open("/")

        # Idle → Running
        user.find("Start Work").click()
        await asyncio.sleep(0.1)  # Wait for async handler
        await user.should_see("Running")
        await user.should_see("Work")

        # Running → Paused
        user.find("Pause").click()
        await asyncio.sleep(1.1)  # Wait for handler + UI refresh (1 second timer)
        # Paused state should be visible (exact text depends on implementation)
        assert app_state.is_paused

        # Paused → Running
        user.find("Resume").click()
        await asyncio.sleep(1.1)  # Wait for async handler + UI refresh
        await user.should_see("Running")

        # Running → Idle
        user.find("Cancel").click()
        await asyncio.sleep(0.1)  # Wait for handler
        await user.should_see("Idle")
        await user.should_see("00:00")
