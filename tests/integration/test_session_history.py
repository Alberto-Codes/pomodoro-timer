"""Integration tests for session history persistence."""

from datetime import datetime, timedelta

import pytest

from pomodoro_timer.models.types import SessionType
from pomodoro_timer.ui.models import CompletedSession
from pomodoro_timer.ui.state import AppState


class TestSessionPersistence:
    """Test session persistence to database."""

    def test_record_completion_saves_work_session_to_database(self, temp_database):
        """Test that completed work sessions are saved to database."""
        # Arrange
        app_state = AppState()
        app_state._database = temp_database
        
        # Manually create a completed session
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=25)
        completed = CompletedSession(
            id=None,
            session_type=SessionType.WORK,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=1500
        )
        
        # Insert into database via app_state's database
        session_id = temp_database.insert(completed)
        
        # Act - Query from database
        sessions = temp_database.query_all()
        
        # Assert
        assert len(sessions) == 1
        assert sessions[0].session_type == SessionType.WORK
        assert sessions[0].duration_seconds == 1500
        assert sessions[0].id == session_id

    def test_record_completion_saves_break_session_to_database(self, temp_database):
        """Test that completed break sessions are saved to database."""
        # Arrange
        app_state = AppState()
        app_state._database = temp_database
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=5)
        completed = CompletedSession(
            id=None,
            session_type=SessionType.BREAK,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=300
        )
        
        temp_database.insert(completed)
        sessions = temp_database.query_all()
        
        # Assert
        assert len(sessions) == 1
        assert sessions[0].session_type == SessionType.BREAK
        assert sessions[0].duration_seconds == 300


class TestHistoryLoading:
    """Test loading history from database."""

    def test_load_history_returns_sessions_in_chronological_order(self, temp_database):
        """Test history loaded in most-recent-first order."""
        # Arrange
        app_state = AppState()
        app_state._database = temp_database
        
        # Create 3 sessions at different times
        now = datetime.now()
        sessions = [
            CompletedSession(
                id=None,
                session_type=SessionType.WORK,
                start_time=now - timedelta(hours=2),
                end_time=now - timedelta(hours=2) + timedelta(minutes=25),
                duration_seconds=1500
            ),
            CompletedSession(
                id=None,
                session_type=SessionType.BREAK,
                start_time=now - timedelta(hours=1),
                end_time=now - timedelta(hours=1) + timedelta(minutes=5),
                duration_seconds=300
            ),
            CompletedSession(
                id=None,
                session_type=SessionType.WORK,
                start_time=now,
                end_time=now + timedelta(minutes=25),
                duration_seconds=1500
            ),
        ]
        
        for session in sessions:
            temp_database.insert(session)
        
        # Act
        loaded = app_state.load_history()
        
        # Assert - Most recent first
        assert len(loaded) == 3
        assert loaded[0].start_time > loaded[1].start_time
        assert loaded[1].start_time > loaded[2].start_time

    def test_load_history_respects_pagination_limit(self, temp_database):
        """Test that load_history respects the limit parameter."""
        # Arrange
        app_state = AppState()
        app_state._database = temp_database
        
        # Create 5 sessions
        now = datetime.now()
        for i in range(5):
            session = CompletedSession(
                id=None,
                session_type=SessionType.WORK,
                start_time=now - timedelta(hours=i),
                end_time=now - timedelta(hours=i) + timedelta(minutes=25),
                duration_seconds=1500
            )
            temp_database.insert(session)
        
        # Act - Limit to 3
        loaded = app_state.load_history(limit=3)
        
        # Assert
        assert len(loaded) == 3

    def test_load_history_respects_pagination_offset(self, temp_database):
        """Test that load_history respects the offset parameter."""
        # Arrange
        app_state = AppState()
        app_state._database = temp_database
        
        # Create 5 sessions
        now = datetime.now()
        for i in range(5):
            session = CompletedSession(
                id=None,
                session_type=SessionType.WORK,
                start_time=now - timedelta(hours=i),
                end_time=now - timedelta(hours=i) + timedelta(minutes=25),
                duration_seconds=1500
            )
            temp_database.insert(session)
        
        # Act - Skip first 2, get 3
        loaded = app_state.load_history(limit=3, offset=2)
        
        # Assert
        assert len(loaded) == 3


class TestDateGrouping:
    """Test filtering sessions by date."""

    def test_get_history_by_date_returns_only_sessions_from_that_date(self, temp_database):
        """Test date filtering returns only sessions from specified date."""
        # Arrange
        app_state = AppState()
        app_state._database = temp_database
        
        today = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        
        # Create sessions on different days
        today_session = CompletedSession(
            id=None,
            session_type=SessionType.WORK,
            start_time=today,
            end_time=today + timedelta(minutes=25),
            duration_seconds=1500
        )
        yesterday_session = CompletedSession(
            id=None,
            session_type=SessionType.WORK,
            start_time=yesterday,
            end_time=yesterday + timedelta(minutes=25),
            duration_seconds=1500
        )
        
        temp_database.insert(today_session)
        temp_database.insert(yesterday_session)
        
        # Act - Filter by today
        today_sessions = app_state.get_history_by_date(today)
        
        # Assert
        assert len(today_sessions) == 1
        assert today_sessions[0].start_time.date() == today.date()

    def test_get_history_by_date_returns_empty_list_for_no_sessions(self, temp_database):
        """Test date filtering returns empty list when no sessions exist."""
        # Arrange
        app_state = AppState()
        app_state._database = temp_database
        
        future_date = datetime.now() + timedelta(days=30)
        
        # Act
        sessions = app_state.get_history_by_date(future_date)
        
        # Assert
        assert len(sessions) == 0


@pytest.fixture
def temp_database(tmp_path):
    """Create a temporary database for testing."""
    from pomodoro_timer.ui.database import SessionDatabase
    db_path = tmp_path / "test_sessions.db"
    return SessionDatabase(db_path)
