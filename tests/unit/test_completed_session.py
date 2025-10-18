"""Unit tests for CompletedSession model."""

import sqlite3
from datetime import datetime

import pytest

from pomodoro_timer.models.session import TimerSession
from pomodoro_timer.models.types import SessionType
from pomodoro_timer.ui.models import CompletedSession


class TestCompletedSessionFactoryMethods:
    """Test CompletedSession factory methods."""
    
    def test_from_session_creates_completed_session(self):
        """Test creating CompletedSession from active session."""
        # Given: A completed work session
        session = TimerSession()
        session.start_work()
        
        # When: Creating CompletedSession from it
        completed = CompletedSession.from_session(session)
        
        # Then: CompletedSession is created with correct type
        assert completed.session_type == SessionType.WORK
        assert completed.id is None  # Not yet persisted
        assert completed.duration_seconds > 0
        assert isinstance(completed.start_time, datetime)
        assert isinstance(completed.end_time, datetime)
    
    def test_from_session_raises_without_type(self):
        """Test that from_session raises error if session has no type."""
        # Given: An idle session without type
        session = TimerSession()
        
        # When/Then: Creating CompletedSession raises ValueError
        with pytest.raises(ValueError, match="without type"):
            CompletedSession.from_session(session)
    
    def test_from_session_raises_without_start_time(self):
        """Test that from_session raises error if session has no start_time."""
        # Given: A session with type but no start_time (edge case)
        session = TimerSession()
        session.session_type = SessionType.WORK
        session.start_time = None
        
        # When/Then: Creating CompletedSession raises ValueError
        with pytest.raises(ValueError, match="without start_time"):
            CompletedSession.from_session(session)
    
    def test_from_db_row_creates_completed_session(self):
        """Test creating CompletedSession from database row."""
        # Given: A mock database row
        start_time = datetime(2025, 10, 18, 10, 0, 0)
        end_time = datetime(2025, 10, 18, 10, 25, 0)
        
        # Create a mock sqlite3.Row
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE temp (
                id INTEGER,
                session_type TEXT,
                start_time REAL,
                end_time REAL,
                duration_seconds INTEGER
            )
        """)
        cursor.execute(
            "INSERT INTO temp VALUES (?, ?, ?, ?, ?)",
            (1, "WORK", start_time.timestamp(), end_time.timestamp(), 1500)
        )
        row = cursor.execute("SELECT * FROM temp").fetchone()
        
        # When: Creating CompletedSession from row
        completed = CompletedSession.from_db_row(row)
        
        # Then: CompletedSession has correct values
        assert completed.id == 1
        assert completed.session_type == SessionType.WORK
        assert completed.start_time == start_time
        assert completed.end_time == end_time
        assert completed.duration_seconds == 1500


class TestCompletedSessionComputedProperties:
    """Test CompletedSession computed properties."""
    
    def test_duration_display_formats_minutes(self):
        """Test duration_display property formats as minutes."""
        # Given: A 25-minute work session
        completed = CompletedSession(
            id=1,
            session_type=SessionType.WORK,
            start_time=datetime(2025, 10, 18, 10, 0, 0),
            end_time=datetime(2025, 10, 18, 10, 25, 0),
            duration_seconds=1500,
        )
        
        # When/Then: Duration displays as "25 min"
        assert completed.duration_display == "25 min"
    
    def test_duration_display_for_break_session(self):
        """Test duration_display for short break."""
        # Given: A 5-minute break session
        completed = CompletedSession(
            id=2,
            session_type=SessionType.BREAK,
            start_time=datetime(2025, 10, 18, 10, 25, 0),
            end_time=datetime(2025, 10, 18, 10, 30, 0),
            duration_seconds=300,
        )
        
        # When/Then: Duration displays as "5 min"
        assert completed.duration_display == "5 min"
    
    def test_date_property_returns_date_portion(self):
        """Test date property extracts date from start_time."""
        # Given: A session starting at a specific date/time
        completed = CompletedSession(
            id=1,
            session_type=SessionType.WORK,
            start_time=datetime(2025, 10, 18, 14, 30, 0),
            end_time=datetime(2025, 10, 18, 14, 55, 0),
            duration_seconds=1500,
        )
        
        # When/Then: Date property returns just the date
        assert completed.date == datetime(2025, 10, 18).date()
    
    def test_time_range_display_formats_hh_mm(self):
        """Test time_range_display property formats as HH:MM - HH:MM."""
        # Given: A session with specific start/end times
        completed = CompletedSession(
            id=1,
            session_type=SessionType.WORK,
            start_time=datetime(2025, 10, 18, 9, 15, 0),
            end_time=datetime(2025, 10, 18, 9, 40, 0),
            duration_seconds=1500,
        )
        
        # When/Then: Time range displays correctly
        assert completed.time_range_display == "09:15 - 09:40"
    
    def test_time_range_display_with_afternoon_times(self):
        """Test time_range_display with PM times."""
        # Given: An afternoon session
        completed = CompletedSession(
            id=1,
            session_type=SessionType.WORK,
            start_time=datetime(2025, 10, 18, 14, 0, 0),
            end_time=datetime(2025, 10, 18, 14, 25, 0),
            duration_seconds=1500,
        )
        
        # When/Then: Time range displays with 24-hour format
        assert completed.time_range_display == "14:00 - 14:25"


class TestCompletedSessionValidation:
    """Test CompletedSession validation (implicit via dataclass)."""
    
    def test_completed_session_creation_with_all_fields(self):
        """Test creating CompletedSession with all required fields."""
        # Given/When: Creating a CompletedSession
        completed = CompletedSession(
            id=1,
            session_type=SessionType.WORK,
            start_time=datetime(2025, 10, 18, 10, 0, 0),
            end_time=datetime(2025, 10, 18, 10, 25, 0),
            duration_seconds=1500,
        )
        
        # Then: All fields are set correctly
        assert completed.id == 1
        assert completed.session_type == SessionType.WORK
        assert completed.duration_seconds == 1500
    
    def test_completed_session_with_none_id(self):
        """Test creating CompletedSession with None id (before persistence)."""
        # Given/When: Creating CompletedSession without database ID
        completed = CompletedSession(
            id=None,
            session_type=SessionType.BREAK,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=300,
        )
        
        # Then: ID is None as expected
        assert completed.id is None
        assert completed.session_type == SessionType.BREAK
