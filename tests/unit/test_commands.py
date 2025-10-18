"""Unit tests for CLI command handlers."""

import argparse

import pytest

from pomodoro_timer.cli.commands import (
    create_parser,
    handle_cancel,
    handle_pause,
    handle_resume,
    handle_start,
    handle_status,
    run_command,
)
from pomodoro_timer.models.session import TimerSession
from pomodoro_timer.models.types import SessionState, SessionType


class TestCreateParser:
    """Tests for create_parser() function."""

    def test_parser_creation(self):
        """Test that create_parser returns ArgumentParser instance."""
        parser = create_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_parser_has_start_command(self):
        """Test that parser has start subcommand."""
        parser = create_parser()
        args = parser.parse_args(["start", "work"])
        assert args.command == "start"
        assert args.session_type == "work"

    def test_parser_start_accepts_work(self):
        """Test that start command accepts 'work' session type."""
        parser = create_parser()
        args = parser.parse_args(["start", "work"])
        assert args.session_type == "work"

    def test_parser_start_accepts_break(self):
        """Test that start command accepts 'break' session type."""
        parser = create_parser()
        args = parser.parse_args(["start", "break"])
        assert args.session_type == "break"

    def test_parser_has_pause_command(self):
        """Test that parser has pause subcommand."""
        parser = create_parser()
        args = parser.parse_args(["pause"])
        assert args.command == "pause"

    def test_parser_has_resume_command(self):
        """Test that parser has resume subcommand."""
        parser = create_parser()
        args = parser.parse_args(["resume"])
        assert args.command == "resume"

    def test_parser_has_cancel_command(self):
        """Test that parser has cancel subcommand."""
        parser = create_parser()
        args = parser.parse_args(["cancel"])
        assert args.command == "cancel"

    def test_parser_has_status_command(self):
        """Test that parser has status subcommand."""
        parser = create_parser()
        args = parser.parse_args(["status"])
        assert args.command == "status"


class TestHandleStart:
    """Tests for handle_start() function."""

    @pytest.mark.asyncio
    async def test_handle_start_work_success(self):
        """Test handling start work command successfully."""
        session = TimerSession()
        
        # Run briefly and stop
        import asyncio
        task = asyncio.create_task(handle_start(session, "work"))
        await asyncio.sleep(0.2)
        
        # Stop the engine by cancelling
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        assert session.session_type == SessionType.WORK

    @pytest.mark.asyncio
    async def test_handle_start_break_success(self):
        """Test handling start break command successfully."""
        session = TimerSession()
        
        # Run briefly and stop
        import asyncio
        task = asyncio.create_task(handle_start(session, "break"))
        await asyncio.sleep(0.2)
        
        # Stop the engine by cancelling
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        assert session.session_type == SessionType.BREAK

    @pytest.mark.asyncio
    async def test_handle_start_returns_error_when_already_active(self):
        """Test that handle_start returns error code when session already active."""
        session = TimerSession()
        session.start_work()
        
        result = await handle_start(session, "work")
        
        assert result == 2


class TestHandleStatus:
    """Tests for handle_status() function."""

    def test_handle_status_idle_session(self, capsys):
        """Test status display for idle session."""
        session = TimerSession()
        
        result = handle_status(session)
        
        assert result == 0
        captured = capsys.readouterr()
        assert "State:" in captured.out
        assert "No active session" in captured.out

    def test_handle_status_running_work_session(self, capsys):
        """Test status display for running work session."""
        session = TimerSession()
        session.start_work()
        
        result = handle_status(session)
        
        assert result == 0
        captured = capsys.readouterr()
        assert "State:" in captured.out
        assert "Session Type:" in captured.out
        assert "Remaining Time:" in captured.out
        assert "Work" in captured.out

    def test_handle_status_paused_break_session(self, capsys):
        """Test status display for paused break session."""
        session = TimerSession()
        session.start_break()
        session.pause()
        
        result = handle_status(session)
        
        assert result == 0
        captured = capsys.readouterr()
        assert "State:" in captured.out
        assert "Session Type:" in captured.out
        assert "Break" in captured.out


class TestHandlePause:
    """Tests for handle_pause() function."""

    def test_handle_pause_success(self, capsys):
        """Test pausing a running session successfully."""
        session = TimerSession()
        session.start_work()
        
        result = handle_pause(session)
        
        assert result == 0
        assert session.state == SessionState.PAUSED
        captured = capsys.readouterr()
        assert "Timer paused" in captured.out

    def test_handle_pause_error_when_not_running(self, capsys):
        """Test pause returns error when session not running."""
        session = TimerSession()
        
        result = handle_pause(session)
        
        assert result == 2
        captured = capsys.readouterr()
        assert "Error:" in captured.err


class TestHandleResume:
    """Tests for handle_resume() function."""

    @pytest.mark.asyncio
    async def test_handle_resume_success(self):
        """Test resuming a paused session successfully."""
        session = TimerSession()
        session.start_work()
        session.pause()
        
        # Run briefly and stop
        import asyncio
        task = asyncio.create_task(handle_resume(session))
        await asyncio.sleep(0.2)
        
        # Cancel to stop the countdown
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_handle_resume_error_when_not_paused(self, capsys):
        """Test resume returns error when session not paused."""
        session = TimerSession()
        
        result = await handle_resume(session)
        
        assert result == 2
        captured = capsys.readouterr()
        assert "Error:" in captured.err


class TestHandleCancel:
    """Tests for handle_cancel() function."""

    def test_handle_cancel_success(self, capsys):
        """Test canceling a session successfully."""
        session = TimerSession()
        session.start_work()
        
        result = handle_cancel(session)
        
        assert result == 0
        assert session.state == SessionState.IDLE
        captured = capsys.readouterr()
        assert "Timer canceled" in captured.out

    def test_handle_cancel_from_idle(self, capsys):
        """Test canceling from idle state."""
        session = TimerSession()
        
        result = handle_cancel(session)
        
        assert result == 0
        assert session.state == SessionState.IDLE


class TestRunCommand:
    """Tests for run_command() function."""

    @pytest.mark.asyncio
    async def test_run_command_start_work(self):
        """Test running start work command."""
        args = argparse.Namespace(command="start", session_type="work")
        
        # We need to cancel the task since it will run indefinitely
        import asyncio
        task = asyncio.create_task(run_command(args))
        await asyncio.sleep(0.2)
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_run_command_start_break(self):
        """Test running start break command."""
        args = argparse.Namespace(command="start", session_type="break")
        
        # We need to cancel the task since it will run indefinitely
        import asyncio
        task = asyncio.create_task(run_command(args))
        await asyncio.sleep(0.2)
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_run_command_status(self, capsys):
        """Test running status command."""
        args = argparse.Namespace(command="status")
        
        result = await run_command(args)
        
        assert result == 0

    @pytest.mark.asyncio
    async def test_run_command_pause(self):
        """Test running pause command on idle session."""
        args = argparse.Namespace(command="pause")
        
        result = await run_command(args)
        
        # Should return error since no active session
        assert result == 2

    @pytest.mark.asyncio
    async def test_run_command_resume(self):
        """Test running resume command on idle session."""
        args = argparse.Namespace(command="resume")
        
        result = await run_command(args)
        
        # Should return error since no paused session
        assert result == 2

    @pytest.mark.asyncio
    async def test_run_command_cancel(self, capsys):
        """Test running cancel command."""
        args = argparse.Namespace(command="cancel")
        
        result = await run_command(args)
        
        assert result == 0

    @pytest.mark.asyncio
    async def test_run_command_no_command(self, capsys):
        """Test running with no command specified."""
        args = argparse.Namespace(command=None)
        
        result = await run_command(args)
        
        assert result == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err
        assert "No command specified" in captured.err
