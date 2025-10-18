"""Database management for session history.

This module provides SQLite database operations for persisting completed sessions.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

from pomodoro_timer.ui.models import CompletedSession


class SessionDatabase:
    """Manages SQLite database for session history.
    
    Attributes:
        db_path: Path to the SQLite database file
    """
    
    def __init__(self, db_path: Path | None = None) -> None:
        """Initialize database connection.
        
        Args:
            db_path: Path to database file. If None, uses default location:
                     ~/.local/share/pomodoro-timer/sessions.db
        """
        if db_path is None:
            # Use XDG Base Directory specification
            data_dir = Path.home() / ".local" / "share" / "pomodoro-timer"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "sessions.db"
        
        self.db_path = db_path
        self._initialize_schema()
    
    def _initialize_schema(self) -> None:
        """Create database schema if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_type TEXT NOT NULL CHECK(session_type IN ('WORK', 'BREAK')),
                    start_time REAL NOT NULL,
                    end_time REAL NOT NULL,
                    duration_seconds INTEGER NOT NULL CHECK(duration_seconds > 0),
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)
            
            # Create indexes for efficient querying
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_type 
                ON sessions(session_type)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON sessions(created_at DESC)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_start_time 
                ON sessions(start_time DESC)
            """)
            conn.commit()
    
    def insert(self, session: CompletedSession) -> int:
        """Insert a completed session into the database.
        
        Args:
            session: The completed session to save
            
        Returns:
            Database ID of the inserted session
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO sessions (session_type, start_time, end_time, duration_seconds)
                VALUES (?, ?, ?, ?)
                """,
                (
                    session.session_type.name,
                    session.start_time.timestamp(),
                    session.end_time.timestamp(),
                    session.duration_seconds,
                ),
            )
            conn.commit()
            return cursor.lastrowid
    
    def query_all(self, limit: int = 100, offset: int = 0) -> list[CompletedSession]:
        """Query all sessions ordered by start time (most recent first).
        
        Args:
            limit: Maximum number of sessions to return (default: 100)
            offset: Number of sessions to skip (for pagination, default: 0)
            
        Returns:
            List of CompletedSession objects
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT id, session_type, start_time, end_time, duration_seconds
                FROM sessions
                ORDER BY start_time DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )
            return [CompletedSession.from_db_row(row) for row in cursor.fetchall()]
    
    def query_by_date(self, date: datetime) -> list[CompletedSession]:
        """Query sessions for a specific date.
        
        Args:
            date: Date to query sessions for
            
        Returns:
            List of CompletedSession objects for that date
        """
        # Get start and end timestamps for the date
        start_of_day = datetime(date.year, date.month, date.day, 0, 0, 0)
        end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT id, session_type, start_time, end_time, duration_seconds
                FROM sessions
                WHERE start_time >= ? AND start_time <= ?
                ORDER BY start_time
                """,
                (start_of_day.timestamp(), end_of_day.timestamp()),
            )
            return [CompletedSession.from_db_row(row) for row in cursor.fetchall()]
    
    def delete_all(self) -> None:
        """Delete all sessions from the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM sessions")
            conn.commit()
    
    def count(self) -> int:
        """Count total number of sessions in database.
        
        Returns:
            Total session count
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM sessions")
            return cursor.fetchone()[0]
