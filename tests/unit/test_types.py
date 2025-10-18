"""Unit tests for SessionType and SessionState enums."""

import pytest

from pomodoro_timer.models.types import SessionState, SessionType


class TestSessionType:
    """Tests for SessionType enum."""

    def test_work_duration_seconds(self):
        """Test WORK session has 1500 seconds (25 minutes)."""
        assert SessionType.WORK.duration_seconds == 1500

    def test_break_duration_seconds(self):
        """Test BREAK session has 300 seconds (5 minutes)."""
        assert SessionType.BREAK.duration_seconds == 300

    def test_work_display_name(self):
        """Test WORK session display name is 'Work'."""
        assert SessionType.WORK.display_name == "Work"

    def test_break_display_name(self):
        """Test BREAK session display name is 'Break'."""
        assert SessionType.BREAK.display_name == "Break"

    def test_enum_values(self):
        """Test enum has exactly two values: WORK and BREAK."""
        assert set(SessionType) == {SessionType.WORK, SessionType.BREAK}


class TestSessionState:
    """Tests for SessionState enum."""

    def test_idle_display_name(self):
        """Test IDLE state display name is 'IDLE'."""
        assert SessionState.IDLE.display_name == "IDLE"

    def test_running_display_name(self):
        """Test RUNNING state display name is 'RUNNING'."""
        assert SessionState.RUNNING.display_name == "RUNNING"

    def test_paused_display_name(self):
        """Test PAUSED state display name is 'PAUSED'."""
        assert SessionState.PAUSED.display_name == "PAUSED"

    def test_completed_display_name(self):
        """Test COMPLETED state display name is 'COMPLETED'."""
        assert SessionState.COMPLETED.display_name == "COMPLETED"

    def test_enum_values(self):
        """Test enum has exactly four states."""
        expected_states = {
            SessionState.IDLE,
            SessionState.RUNNING,
            SessionState.PAUSED,
            SessionState.COMPLETED,
        }
        assert set(SessionState) == expected_states
