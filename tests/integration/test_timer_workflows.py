"""Integration tests for timer workflows and user scenarios."""

import asyncio
import time

import pytest
from freezegun import freeze_time

from pomodoro_timer.models.session import TimerSession
from pomodoro_timer.models.types import SessionState, SessionType


class TestUserStory1AcceptanceScenarios:
    """Integration tests for User Story 1: Start and Complete Work Session."""

    @pytest.mark.asyncio
    async def test_acceptance_scenario_1_start_work_countdown(self):
        """Given the timer is idle,
        When user starts a work session,
        Then the timer begins counting down from 25 minutes (T018).
        """
        session = TimerSession()
        assert session.state == SessionState.IDLE

        # Start work session
        session.start_work()

        # Verify initial state
        assert session.state == SessionState.RUNNING
        assert session.session_type == SessionType.WORK
        assert session.remaining_seconds == 1500

        # Simulate time passing
        await asyncio.sleep(0.1)
        session.tick()

        # Time should have decreased slightly
        assert session.remaining_seconds < 1500
        assert session.state == SessionState.RUNNING

    @freeze_time("2024-01-01 12:00:00")
    def test_acceptance_scenario_2_notify_on_completion(self):
        """Given a work session is running,
        When the timer reaches zero,
        Then the user is notified that the work session is complete (T019).
        """
        session = TimerSession()
        session.start_work()

        # Fast-forward to completion
        with freeze_time("2024-01-01 12:25:00"):
            session.tick()

            # Session should be completed
            assert session.state == SessionState.COMPLETED
            assert session.remaining_seconds == 0

    def test_acceptance_scenario_3_display_remaining_time(self):
        """Given a work session is running,
        When the user checks the timer,
        Then the remaining time is displayed accurately (T020).
        """
        session = TimerSession()
        session.start_work()

        # Check initial time
        assert session.formatted_time == "25:00"

        # Simulate 5 minutes passing
        session.remaining_seconds = 1200  # 20 minutes remaining
        assert session.formatted_time == "20:00"

        # Simulate 1 minute 30 seconds remaining
        session.remaining_seconds = 90
        assert session.formatted_time == "01:30"

        # At completion
        session.remaining_seconds = 0
        assert session.formatted_time == "00:00"


class TestUserStory2AcceptanceScenarios:
    """Integration tests for User Story 2: Take Short Break."""

    def test_acceptance_scenario_1_start_break_after_work(self):
        """Given a work session just completed,
        When the user starts a break,
        Then the timer begins counting down from 5 minutes (T053).
        """
        session = TimerSession()

        # Complete a work session
        session.start_work()
        session.end_time = time.time() - 1
        session.tick()
        assert session.state == SessionState.COMPLETED

        # Start break
        session.start_break()

        assert session.state == SessionState.RUNNING
        assert session.session_type == SessionType.BREAK
        assert session.remaining_seconds == 300

    @freeze_time("2024-01-01 12:00:00")
    def test_acceptance_scenario_2_notify_break_completion(self):
        """Given a break is running,
        When the timer reaches zero,
        Then the user is notified that the break is complete (T054).
        """
        session = TimerSession()
        session.start_break()

        # Fast-forward 5 minutes
        with freeze_time("2024-01-01 12:05:00"):
            session.tick()

            assert session.state == SessionState.COMPLETED
            assert session.remaining_seconds == 0

    def test_acceptance_scenario_3_start_work_after_break(self):
        """Given a break just completed,
        When the user is ready,
        Then they can start a new work session (T055).
        """
        session = TimerSession()

        # Complete a break
        session.start_break()
        session.end_time = time.time() - 1
        session.tick()
        assert session.state == SessionState.COMPLETED

        # Start new work session
        session.start_work()

        assert session.state == SessionState.RUNNING
        assert session.session_type == SessionType.WORK
        assert session.remaining_seconds == 1500

    def test_full_work_break_cycle(self):
        """Test full work-break cycle: work → complete → break → complete → work (T056).
        """
        session = TimerSession()

        # Start work
        session.start_work()
        assert session.session_type == SessionType.WORK

        # Complete work
        session.end_time = time.time() - 1
        session.tick()
        assert session.state == SessionState.COMPLETED

        # Start break
        session.start_break()
        assert session.session_type == SessionType.BREAK

        # Complete break
        session.end_time = time.time() - 1
        session.tick()
        assert session.state == SessionState.COMPLETED

        # Start new work session
        session.start_work()
        assert session.session_type == SessionType.WORK
        assert session.state == SessionState.RUNNING


class TestUserStory3AcceptanceScenarios:
    """Integration tests for User Story 3: Pause and Resume Sessions."""

    def test_acceptance_scenario_1_pause_preserves_time(self):
        """Given a timer is running,
        When the user pauses it,
        Then the countdown stops and preserves the remaining time (T075).
        """
        session = TimerSession()
        session.start_work()

        # Get initial remaining time
        initial_remaining = session.remaining_seconds

        session.pause()

        assert session.state == SessionState.PAUSED
        # Time should be approximately preserved (within 1 second due to execution time)
        assert abs(session.remaining_seconds - initial_remaining) <= 1

    def test_acceptance_scenario_2_resume_continues_countdown(self):
        """Given a timer is paused,
        When the user resumes it,
        Then the countdown continues from where it stopped (T076).
        """
        session = TimerSession()
        session.start_work()

        # Pause with time remaining
        session.remaining_seconds = 1400
        session.pause()
        paused_time = session.remaining_seconds

        # Resume
        session.resume()

        assert session.state == SessionState.RUNNING
        assert session.remaining_seconds == paused_time

    def test_acceptance_scenario_3_display_paused_state(self):
        """Given a timer is paused,
        When the user checks the display,
        Then it shows the paused time and indicates the paused state (T077).
        """
        session = TimerSession()
        session.start_work()

        # Simulate time passing by adjusting end_time
        session.end_time = time.time() + 900  # 15 minutes remaining
        session.tick()  # Update remaining_seconds

        session.pause()

        assert session.state == SessionState.PAUSED
        # Should be approximately 15:00 (allow 1 second variance for execution time)
        assert session.formatted_time in ["14:59", "15:00"]
        assert session.state.display_name == "PAUSED"


class TestUserStory4AcceptanceScenarios:
    """Integration tests for User Story 4: Cancel Active Session."""

    def test_acceptance_scenario_1_cancel_running_or_paused(self):
        """Given a timer is running or paused,
        When the user cancels it,
        Then the timer stops and returns to idle state (T096).
        """
        # Test canceling running session
        session = TimerSession()
        session.start_work()
        assert session.state == SessionState.RUNNING

        session.cancel()
        assert session.state == SessionState.IDLE

        # Test canceling paused session
        session.start_work()
        session.pause()
        assert session.state == SessionState.PAUSED

        session.cancel()
        assert session.state == SessionState.IDLE

    def test_acceptance_scenario_2_start_fresh_after_cancel(self):
        """Given the user canceled a session,
        When they start a new session,
        Then it begins fresh from full duration (T097).
        """
        session = TimerSession()

        # Start and partially complete work session
        session.start_work()
        session.remaining_seconds = 1000

        # Cancel
        session.cancel()

        # Start new work session
        session.start_work()

        # Should start from full 25 minutes
        assert session.remaining_seconds == 1500
        assert session.state == SessionState.RUNNING
