"""Unit tests for TimerSession class."""

import time

import pytest

from pomodoro_timer.models.exceptions import InvalidStateTransition, SessionAlreadyActive
from pomodoro_timer.models.session import TimerSession
from pomodoro_timer.models.types import SessionState, SessionType


class TestTimerSessionInitialization:
    """Tests for TimerSession initialization (T013)."""

    def test_new_session_is_idle(self):
        """Test new session should be in IDLE state."""
        session = TimerSession()
        assert session.state == SessionState.IDLE

    def test_new_session_has_no_type(self):
        """Test new session has no session type set."""
        session = TimerSession()
        assert session.session_type is None

    def test_new_session_has_zero_remaining_seconds(self):
        """Test new session has zero remaining seconds."""
        session = TimerSession()
        assert session.remaining_seconds == 0

    def test_new_session_has_no_timestamps(self):
        """Test new session has no start or end timestamps."""
        session = TimerSession()
        assert session.start_time is None
        assert session.end_time is None


class TestTimerSessionStartWork:
    """Tests for TimerSession.start_work() method (T014, T015)."""

    def test_start_work_from_idle_state(self):
        """Test start_work() transitions from IDLE to RUNNING (T014)."""
        session = TimerSession()
        session.start_work()

        assert session.state == SessionState.RUNNING
        assert session.session_type == SessionType.WORK
        assert session.remaining_seconds == 1500
        assert session.start_time is not None
        assert session.end_time is not None

    def test_start_work_sets_correct_end_time(self):
        """Test start_work() sets end_time to start_time + 1500 seconds."""
        session = TimerSession()
        start = time.time()
        session.start_work()

        # Allow small delta for execution time
        expected_end = start + 1500
        assert abs(session.end_time - expected_end) < 0.1

    def test_start_work_raises_when_running(self):
        """Test start_work() raises SessionAlreadyActive when session already running (T015)."""
        session = TimerSession()
        session.start_work()

        with pytest.raises(SessionAlreadyActive):
            session.start_work()

    def test_start_work_raises_when_paused(self):
        """Test start_work() raises SessionAlreadyActive when session is paused."""
        session = TimerSession()
        session.start_work()
        session.pause()

        with pytest.raises(SessionAlreadyActive):
            session.start_work()


class TestTimerSessionTick:
    """Tests for TimerSession.tick() method (T016)."""

    def test_tick_decreases_remaining_seconds(self):
        """Test tick() decreases remaining_seconds based on elapsed time."""
        session = TimerSession()
        session.start_work()

        # Simulate 2 seconds passing
        session.end_time = time.time() + 1498  # 2 seconds less than original 1500
        session.tick()

        assert 1497 <= session.remaining_seconds <= 1499

    def test_tick_transitions_to_completed_at_zero(self):
        """Test tick() transitions to COMPLETED when time reaches zero."""
        session = TimerSession()
        session.start_work()

        # Set end_time to past
        session.end_time = time.time() - 1
        session.tick()

        assert session.state == SessionState.COMPLETED
        assert session.remaining_seconds == 0

    def test_tick_does_nothing_when_not_running(self):
        """Test tick() does nothing when state is not RUNNING."""
        session = TimerSession()
        session.tick()  # Should not raise error

        assert session.state == SessionState.IDLE


class TestTimerSessionStateMachine:
    """Tests for state machine transitions (T017)."""

    def test_idle_to_running_transition(self):
        """Test valid transition: IDLE → RUNNING."""
        session = TimerSession()
        assert session.state == SessionState.IDLE

        session.start_work()
        assert session.state == SessionState.RUNNING

    def test_running_to_completed_transition(self):
        """Test valid transition: RUNNING → COMPLETED."""
        session = TimerSession()
        session.start_work()

        # Force completion
        session.end_time = time.time() - 1
        session.tick()

        assert session.state == SessionState.COMPLETED

    def test_completed_to_idle_via_cancel(self):
        """Test valid transition: COMPLETED → IDLE via cancel."""
        session = TimerSession()
        session.start_work()
        session.end_time = time.time() - 1
        session.tick()

        session.cancel()
        assert session.state == SessionState.IDLE

    def test_completed_to_running_via_start_work(self):
        """Test valid transition: COMPLETED → RUNNING via start_work."""
        session = TimerSession()
        session.start_work()
        session.end_time = time.time() - 1
        session.tick()

        assert session.state == SessionState.COMPLETED

        session.start_work()
        assert session.state == SessionState.RUNNING


class TestTimerSessionPause:
    """Tests for TimerSession.pause() method (for US3, pre-implemented test)."""

    def test_pause_from_running_state(self):
        """Test pause() transitions from RUNNING to PAUSED."""
        session = TimerSession()
        session.start_work()

        session.pause()
        assert session.state == SessionState.PAUSED
        assert session.remaining_seconds > 0

    def test_pause_raises_when_not_running(self):
        """Test pause() raises InvalidStateTransition when not RUNNING."""
        session = TimerSession()

        with pytest.raises(InvalidStateTransition):
            session.pause()


class TestTimerSessionResume:
    """Tests for TimerSession.resume() method (for US3, pre-implemented test)."""

    def test_resume_from_paused_state(self):
        """Test resume() transitions from PAUSED to RUNNING."""
        session = TimerSession()
        session.start_work()
        session.pause()

        session.resume()
        assert session.state == SessionState.RUNNING

    def test_resume_raises_when_not_paused(self):
        """Test resume() raises InvalidStateTransition when not PAUSED."""
        session = TimerSession()

        with pytest.raises(InvalidStateTransition):
            session.resume()


class TestTimerSessionCancel:
    """Tests for TimerSession.cancel() method (for US4, pre-implemented test)."""

    def test_cancel_from_running_state(self):
        """Test cancel() transitions from RUNNING to IDLE."""
        session = TimerSession()
        session.start_work()

        session.cancel()
        assert session.state == SessionState.IDLE

    def test_cancel_from_paused_state(self):
        """Test cancel() transitions from PAUSED to IDLE."""
        session = TimerSession()
        session.start_work()
        session.pause()

        session.cancel()
        assert session.state == SessionState.IDLE


class TestTimerSessionProperties:
    """Tests for TimerSession properties."""

    def test_formatted_time_displays_mm_ss(self):
        """Test formatted_time property returns MM:SS format."""
        session = TimerSession()
        session.start_work()

        # Should be 25:00
        formatted = session.formatted_time
        assert formatted == "25:00"

    def test_formatted_time_with_partial_seconds(self):
        """Test formatted_time handles partial minutes correctly."""
        session = TimerSession()
        session.start_work()
        session.remaining_seconds = 90  # 1 minute 30 seconds

        assert session.formatted_time == "01:30"

    def test_formatted_time_at_zero(self):
        """Test formatted_time shows 00:00 when completed."""
        session = TimerSession()
        session.start_work()
        session.end_time = time.time() - 1
        session.tick()

        assert session.formatted_time == "00:00"

    def test_is_active_when_running(self):
        """Test is_active property is True when RUNNING."""
        session = TimerSession()
        session.start_work()

        assert session.is_active is True

    def test_is_active_when_paused(self):
        """Test is_active property is True when PAUSED."""
        session = TimerSession()
        session.start_work()
        session.pause()

        assert session.is_active is True

    def test_is_active_when_idle(self):
        """Test is_active property is False when IDLE."""
        session = TimerSession()

        assert session.is_active is False

    def test_is_active_when_completed(self):
        """Test is_active property is False when COMPLETED."""
        session = TimerSession()
        session.start_work()
        session.end_time = time.time() - 1
        session.tick()

        assert session.is_active is False
