"""Unit tests for TimerEngine class."""

import asyncio

import pytest
from freezegun import freeze_time

from pomodoro_timer.models.exceptions import SessionAlreadyActive
from pomodoro_timer.models.session import TimerSession
from pomodoro_timer.models.types import SessionState, SessionType
from pomodoro_timer.timer.engine import TimerEngine


class TestTimerEngineInitialization:
    """Tests for TimerEngine initialization."""

    def test_engine_initialization(self):
        """Test that engine initializes with a session."""
        session = TimerSession()
        engine = TimerEngine(session)
        
        assert engine.session is session
        assert engine._running is False


class TestTimerEngineStartWork:
    """Tests for TimerEngine.start_work() method."""

    @pytest.mark.asyncio
    async def test_start_work_initializes_session(self):
        """Test that start_work initializes the session."""
        session = TimerSession()
        engine = TimerEngine(session)
        
        # Start and immediately stop to test initialization
        task = asyncio.create_task(engine.start_work())
        await asyncio.sleep(0.2)  # Let it run briefly
        engine._running = False
        await task
        
        assert session.session_type == SessionType.WORK
        assert session.state in (SessionState.RUNNING, SessionState.COMPLETED)

    @pytest.mark.asyncio
    async def test_start_work_raises_when_already_active(self):
        """Test that start_work raises when session already active."""
        session = TimerSession()
        session.start_work()
        engine = TimerEngine(session)
        
        with pytest.raises(SessionAlreadyActive):
            await engine.start_work()


class TestTimerEngineStartBreak:
    """Tests for TimerEngine.start_break() method."""

    @pytest.mark.asyncio
    async def test_start_break_initializes_session(self):
        """Test that start_break initializes the session."""
        session = TimerSession()
        engine = TimerEngine(session)
        
        # Start and immediately stop to test initialization
        task = asyncio.create_task(engine.start_break())
        await asyncio.sleep(0.2)  # Let it run briefly
        engine._running = False
        await task
        
        assert session.session_type == SessionType.BREAK
        assert session.state in (SessionState.RUNNING, SessionState.COMPLETED)

    @pytest.mark.asyncio
    async def test_start_break_raises_when_already_active(self):
        """Test that start_break raises when session already active."""
        session = TimerSession()
        session.start_work()
        engine = TimerEngine(session)
        
        with pytest.raises(SessionAlreadyActive):
            await engine.start_break()


class TestTimerEnginePause:
    """Tests for TimerEngine.pause() method."""

    def test_pause_pauses_session(self):
        """Test that pause pauses the session."""
        session = TimerSession()
        session.start_work()
        engine = TimerEngine(session)
        engine._running = True
        
        engine.pause()
        
        assert session.state == SessionState.PAUSED
        assert engine._running is False


class TestTimerEngineResume:
    """Tests for TimerEngine.resume() method."""

    @pytest.mark.asyncio
    async def test_resume_resumes_session(self):
        """Test that resume resumes the session."""
        session = TimerSession()
        session.start_work()
        session.pause()
        engine = TimerEngine(session)
        
        # Start resume and immediately stop
        task = asyncio.create_task(engine.resume())
        await asyncio.sleep(0.2)
        engine._running = False
        await task
        
        assert session.state in (SessionState.RUNNING, SessionState.COMPLETED)


class TestTimerEngineCancel:
    """Tests for TimerEngine.cancel() method."""

    def test_cancel_cancels_session(self):
        """Test that cancel cancels the session."""
        session = TimerSession()
        session.start_work()
        engine = TimerEngine(session)
        engine._running = True
        
        engine.cancel()
        
        assert session.state == SessionState.IDLE
        assert engine._running is False


class TestTimerEngineCountdown:
    """Tests for TimerEngine countdown loop behavior."""

    @pytest.mark.asyncio
    async def test_countdown_updates_session(self):
        """Test that countdown loop updates session time."""
        session = TimerSession()
        engine = TimerEngine(session)
        
        initial_time = 1500  # Full work session
        task = asyncio.create_task(engine.start_work())
        
        # Let it run for a bit
        await asyncio.sleep(0.3)
        engine._running = False
        
        try:
            await asyncio.wait_for(task, timeout=2.0)
        except asyncio.TimeoutError:
            pass
        
        # Time should have decreased from initial
        assert session.remaining_seconds < initial_time

    @pytest.mark.asyncio
    async def test_countdown_stops_when_running_flag_false(self):
        """Test that countdown stops when _running flag is set to False."""
        session = TimerSession()
        engine = TimerEngine(session)
        
        task = asyncio.create_task(engine.start_work())
        await asyncio.sleep(0.2)
        
        # Stop the countdown
        engine._running = False
        
        try:
            await asyncio.wait_for(task, timeout=2.0)
        except asyncio.TimeoutError:
            pass
        
        # Should have stopped without completing
        assert session.state == SessionState.RUNNING
