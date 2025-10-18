"""Integration tests for SessionDatabase."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from pomodoro_timer.models.types import SessionType
from pomodoro_timer.ui.database import SessionDatabase
from pomodoro_timer.ui.models import CompletedSession


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_sessions.db"
        yield SessionDatabase(db_path)


class TestSessionDatabaseSchemaInitialization:
    """Test database schema initialization."""
    
    def test_database_creates_sessions_table(self, temp_db):
        """Test that database initializes with sessions table."""
        # Given: A new database instance
        # (created by fixture)
        
        # When: Checking if table exists
        import sqlite3
        with sqlite3.connect(temp_db.db_path) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'"
            )
            table = cursor.fetchone()
        
        # Then: Table exists
        assert table is not None
    
    def test_database_creates_indexes(self, temp_db):
        """Test that database creates required indexes."""
        # Given: A new database instance
        # (created by fixture)
        
        # When: Checking for indexes
        import sqlite3
        with sqlite3.connect(temp_db.db_path) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
            )
            indexes = [row[0] for row in cursor.fetchall()]
        
        # Then: All required indexes exist
        assert "idx_session_type" in indexes
        assert "idx_created_at" in indexes
        assert "idx_start_time" in indexes


class TestSessionDatabaseInsert:
    """Test inserting sessions into database."""
    
    def test_insert_work_session_returns_id(self, temp_db):
        """Test inserting work session returns database ID."""
        # Given: A completed work session
        session = CompletedSession(
            id=None,
            session_type=SessionType.WORK,
            start_time=datetime(2025, 10, 18, 10, 0, 0),
            end_time=datetime(2025, 10, 18, 10, 25, 0),
            duration_seconds=1500,
        )
        
        # When: Inserting session
        session_id = temp_db.insert(session)
        
        # Then: ID is returned
        assert session_id is not None
        assert session_id > 0
    
    def test_insert_break_session(self, temp_db):
        """Test inserting break session."""
        # Given: A completed break session
        session = CompletedSession(
            id=None,
            session_type=SessionType.BREAK,
            start_time=datetime(2025, 10, 18, 10, 25, 0),
            end_time=datetime(2025, 10, 18, 10, 30, 0),
            duration_seconds=300,
        )
        
        # When: Inserting session
        session_id = temp_db.insert(session)
        
        # Then: Session is inserted successfully
        assert session_id > 0
    
    def test_insert_multiple_sessions_returns_unique_ids(self, temp_db):
        """Test inserting multiple sessions returns unique IDs."""
        # Given: Multiple sessions
        sessions = [
            CompletedSession(
                id=None,
                session_type=SessionType.WORK,
                start_time=datetime(2025, 10, 18, i, 0, 0),
                end_time=datetime(2025, 10, 18, i, 25, 0),
                duration_seconds=1500,
            )
            for i in range(9, 12)
        ]
        
        # When: Inserting all sessions
        ids = [temp_db.insert(session) for session in sessions]
        
        # Then: All IDs are unique
        assert len(ids) == len(set(ids))
        assert all(id > 0 for id in ids)


class TestSessionDatabaseQuery:
    """Test querying sessions from database."""
    
    def test_query_all_returns_empty_list_for_new_database(self, temp_db):
        """Test query_all returns empty list when no sessions exist."""
        # Given: Empty database
        # (created by fixture)
        
        # When: Querying all sessions
        sessions = temp_db.query_all()
        
        # Then: Empty list is returned
        assert sessions == []
    
    def test_query_all_returns_inserted_sessions(self, temp_db):
        """Test query_all returns all inserted sessions."""
        # Given: Database with 3 sessions
        for i in range(3):
            session = CompletedSession(
                id=None,
                session_type=SessionType.WORK,
                start_time=datetime(2025, 10, 18, 9 + i, 0, 0),
                end_time=datetime(2025, 10, 18, 9 + i, 25, 0),
                duration_seconds=1500,
            )
            temp_db.insert(session)
        
        # When: Querying all sessions
        sessions = temp_db.query_all()
        
        # Then: 3 sessions are returned
        assert len(sessions) == 3
    
    def test_query_all_orders_by_start_time_descending(self, temp_db):
        """Test query_all returns sessions in reverse chronological order."""
        # Given: Database with sessions at different times
        times = [
            datetime(2025, 10, 18, 9, 0, 0),
            datetime(2025, 10, 18, 11, 0, 0),
            datetime(2025, 10, 18, 10, 0, 0),
        ]
        for start_time in times:
            session = CompletedSession(
                id=None,
                session_type=SessionType.WORK,
                start_time=start_time,
                end_time=start_time.replace(minute=25),
                duration_seconds=1500,
            )
            temp_db.insert(session)
        
        # When: Querying all sessions
        sessions = temp_db.query_all()
        
        # Then: Sessions are ordered by start_time DESC (most recent first)
        assert sessions[0].start_time == datetime(2025, 10, 18, 11, 0, 0)
        assert sessions[1].start_time == datetime(2025, 10, 18, 10, 0, 0)
        assert sessions[2].start_time == datetime(2025, 10, 18, 9, 0, 0)
    
    def test_query_all_respects_limit(self, temp_db):
        """Test query_all limit parameter."""
        # Given: Database with 5 sessions
        for i in range(5):
            session = CompletedSession(
                id=None,
                session_type=SessionType.WORK,
                start_time=datetime(2025, 10, 18, 9 + i, 0, 0),
                end_time=datetime(2025, 10, 18, 9 + i, 25, 0),
                duration_seconds=1500,
            )
            temp_db.insert(session)
        
        # When: Querying with limit=3
        sessions = temp_db.query_all(limit=3)
        
        # Then: Only 3 sessions are returned
        assert len(sessions) == 3
    
    def test_query_all_respects_offset(self, temp_db):
        """Test query_all offset parameter for pagination."""
        # Given: Database with 5 sessions
        for i in range(5):
            session = CompletedSession(
                id=None,
                session_type=SessionType.WORK,
                start_time=datetime(2025, 10, 18, 9 + i, 0, 0),
                end_time=datetime(2025, 10, 18, 9 + i, 25, 0),
                duration_seconds=1500,
            )
            temp_db.insert(session)
        
        # When: Querying with offset=2
        sessions = temp_db.query_all(offset=2)
        
        # Then: First 2 sessions are skipped
        assert len(sessions) == 3
        # Most recent is at 13:00, with offset=2 we start from 11:00
        assert sessions[0].start_time == datetime(2025, 10, 18, 11, 0, 0)


class TestSessionDatabaseQueryByDate:
    """Test querying sessions by date."""
    
    def test_query_by_date_returns_sessions_for_specific_date(self, temp_db):
        """Test query_by_date filters sessions by date."""
        # Given: Database with sessions on different dates
        dates = [
            datetime(2025, 10, 17, 10, 0, 0),
            datetime(2025, 10, 18, 10, 0, 0),
            datetime(2025, 10, 18, 14, 0, 0),
            datetime(2025, 10, 19, 10, 0, 0),
        ]
        for start_time in dates:
            session = CompletedSession(
                id=None,
                session_type=SessionType.WORK,
                start_time=start_time,
                end_time=start_time.replace(minute=25),
                duration_seconds=1500,
            )
            temp_db.insert(session)
        
        # When: Querying for Oct 18
        sessions = temp_db.query_by_date(datetime(2025, 10, 18))
        
        # Then: Only Oct 18 sessions are returned
        assert len(sessions) == 2
        assert all(s.date == datetime(2025, 10, 18).date() for s in sessions)
    
    def test_query_by_date_returns_empty_list_for_no_matches(self, temp_db):
        """Test query_by_date returns empty list when no sessions match."""
        # Given: Database with sessions on Oct 18
        session = CompletedSession(
            id=None,
            session_type=SessionType.WORK,
            start_time=datetime(2025, 10, 18, 10, 0, 0),
            end_time=datetime(2025, 10, 18, 10, 25, 0),
            duration_seconds=1500,
        )
        temp_db.insert(session)
        
        # When: Querying for Oct 19 (no sessions)
        sessions = temp_db.query_by_date(datetime(2025, 10, 19))
        
        # Then: Empty list is returned
        assert sessions == []


class TestSessionDatabaseDelete:
    """Test deleting sessions from database."""
    
    def test_delete_all_removes_all_sessions(self, temp_db):
        """Test delete_all removes all sessions."""
        # Given: Database with sessions
        for i in range(3):
            session = CompletedSession(
                id=None,
                session_type=SessionType.WORK,
                start_time=datetime(2025, 10, 18, 9 + i, 0, 0),
                end_time=datetime(2025, 10, 18, 9 + i, 25, 0),
                duration_seconds=1500,
            )
            temp_db.insert(session)
        
        # When: Deleting all sessions
        temp_db.delete_all()
        
        # Then: No sessions remain
        sessions = temp_db.query_all()
        assert sessions == []
    
    def test_count_returns_correct_number(self, temp_db):
        """Test count method returns correct session count."""
        # Given: Empty database
        assert temp_db.count() == 0
        
        # When: Adding sessions
        for i in range(5):
            session = CompletedSession(
                id=None,
                session_type=SessionType.WORK,
                start_time=datetime(2025, 10, 18, 9 + i, 0, 0),
                end_time=datetime(2025, 10, 18, 9 + i, 25, 0),
                duration_seconds=1500,
            )
            temp_db.insert(session)
        
        # Then: Count is correct
        assert temp_db.count() == 5
