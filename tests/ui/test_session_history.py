"""Acceptance tests for session history view."""

import asyncio
from datetime import datetime, timedelta

import pytest

from pomodoro_timer.models.types import SessionType
from pomodoro_timer.ui.models import CompletedSession
from pomodoro_timer.ui.state import app_state


class TestHistoryView:
    """Test history view displays completed sessions."""

    @pytest.mark.ui
    async def test_history_view_displays_completed_work_session(self, user):
        """Test that completed work sessions appear in history view."""
        # Arrange - Add a completed work session to history
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=25)
        session = CompletedSession(
            id=1,
            session_type=SessionType.WORK,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=1500,
        )
        app_state._history.append(session)

        # Act - Navigate to page (it should show history)
        await user.open("/")

        # Assert - Should see work session in history
        await user.should_see("Work")
        await user.should_see("25 min")

    @pytest.mark.ui
    async def test_history_view_displays_completed_break_session(self, user):
        """Test that completed break sessions appear in history view."""
        # Arrange
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=5)
        session = CompletedSession(
            id=1,
            session_type=SessionType.BREAK,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=300,
        )
        app_state._history.append(session)

        # Act
        await user.open("/")

        # Assert
        await user.should_see("Break")
        await user.should_see("5 min")

    @pytest.mark.ui
    async def test_history_view_displays_multiple_sessions(self, user):
        """Test history displays multiple sessions."""
        # Arrange - Add 3 sessions
        now = datetime.now()
        sessions = [
            CompletedSession(
                id=1,
                session_type=SessionType.WORK,
                start_time=now - timedelta(hours=2),
                end_time=now - timedelta(hours=2) + timedelta(minutes=25),
                duration_seconds=1500,
            ),
            CompletedSession(
                id=2,
                session_type=SessionType.BREAK,
                start_time=now - timedelta(hours=1),
                end_time=now - timedelta(hours=1) + timedelta(minutes=5),
                duration_seconds=300,
            ),
            CompletedSession(
                id=3,
                session_type=SessionType.WORK,
                start_time=now,
                end_time=now + timedelta(minutes=25),
                duration_seconds=1500,
            ),
        ]

        for session in sessions:
            app_state._history.append(session)

        # Act
        await user.open("/")

        # Assert - Should see all 3 sessions
        await user.should_see("Work")
        await user.should_see("Break")


class TestHistoryUpdates:
    """Test that history automatically updates when sessions complete."""

    @pytest.mark.ui
    async def test_history_updates_when_session_completes(self, user):
        """Test history refreshes automatically when new session completes."""
        # Arrange - Start with empty history
        app_state.clear_history()

        # Act - Complete a session by adding to history
        session = CompletedSession(
            id=1,
            session_type=SessionType.WORK,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=25),
            duration_seconds=1500,
        )

        await user.open("/")

        # Add session to observable list (simulating completion)
        app_state._history.append(session)

        # Wait for UI refresh cycle (1 second timer)
        await asyncio.sleep(1.1)

        # Assert - Should see the new session appear
        await user.should_see("Work")
        await user.should_see("25 min")


class TestClearHistory:
    """Test clear history functionality."""

    @pytest.mark.ui
    async def test_clear_history_button_empties_history(self, user):
        """Test clear history button removes all sessions."""
        # Arrange - Add some sessions
        session = CompletedSession(
            id=1,
            session_type=SessionType.WORK,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=25),
            duration_seconds=1500,
        )
        app_state._history.append(session)

        # Act
        await user.open("/")

        # Find and click clear history button (opens confirmation dialog)
        user.find("Clear History").click()
        await asyncio.sleep(0.2)  # Wait for dialog to open

        # Click "Clear All" in confirmation dialog
        user.find("Clear All").click()
        await asyncio.sleep(1.1)  # Wait for clear + UI refresh

        # Assert - History should be empty
        assert len(app_state._history) == 0

    @pytest.mark.ui
    async def test_clear_history_shows_confirmation_dialog(self, user):
        """Test that clear history shows confirmation before deleting."""
        # Arrange
        session = CompletedSession(
            id=1,
            session_type=SessionType.WORK,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=25),
            duration_seconds=1500,
        )
        app_state._history.append(session)

        # Act
        await user.open("/")
        user.find("Clear History").click()

        # Assert - Should see confirmation message
        # (Implementation will determine exact message)
        await user.should_see("Are you sure")
