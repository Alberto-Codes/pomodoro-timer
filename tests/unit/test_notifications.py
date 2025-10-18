"""Unit tests for notification functions."""

import sys
from io import StringIO

import pytest

from pomodoro_timer.models.types import SessionType
from pomodoro_timer.timer.notifications import notify_completion


class TestNotifyCompletion:
    """Tests for notify_completion() function."""

    def test_notify_completion_work_session(self, capsys):
        """Test notification for completed work session."""
        notify_completion(SessionType.WORK)
        
        captured = capsys.readouterr()
        assert "Work session complete" in captured.out
        assert "Time for a break" in captured.out
        assert "✓" in captured.out

    def test_notify_completion_break_session(self, capsys):
        """Test notification for completed break session."""
        notify_completion(SessionType.BREAK)
        
        captured = capsys.readouterr()
        assert "Break complete" in captured.out
        assert "Ready to focus again" in captured.out
        assert "✓" in captured.out

    def test_notify_completion_includes_newline(self, capsys):
        """Test that notification includes newline for proper formatting."""
        notify_completion(SessionType.WORK)
        
        captured = capsys.readouterr()
        assert captured.out.startswith("\n")

    def test_notify_completion_writes_terminal_bell(self, monkeypatch):
        """Test that notification writes terminal bell character."""
        output = StringIO()
        monkeypatch.setattr(sys, "stdout", output)
        
        notify_completion(SessionType.WORK)
        
        result = output.getvalue()
        # Check for bell character (ASCII 7, \a)
        assert "\a" in result

    def test_notify_completion_flushes_output_after_bell(self, monkeypatch):
        """Test that notification flushes stdout after bell."""
        flush_called = False
        original_write = sys.stdout.write
        
        def mock_flush():
            nonlocal flush_called
            flush_called = True
        
        monkeypatch.setattr(sys.stdout, "flush", mock_flush)
        
        notify_completion(SessionType.WORK)
        
        assert flush_called

    def test_notify_completion_handles_bell_exception_gracefully(self, monkeypatch):
        """Test that notification handles exceptions from bell write gracefully."""
        def mock_write_raises(text):
            if text == "\a":
                raise OSError("Terminal does not support bell")
            sys.__stdout__.write(text)
        
        monkeypatch.setattr(sys.stdout, "write", mock_write_raises)
        
        # Should not raise exception
        try:
            notify_completion(SessionType.WORK)
        except Exception as e:
            pytest.fail(f"notify_completion raised unexpected exception: {e}")

    def test_notify_completion_different_messages_for_types(self, capsys):
        """Test that work and break have different messages."""
        notify_completion(SessionType.WORK)
        work_output = capsys.readouterr().out
        
        notify_completion(SessionType.BREAK)
        break_output = capsys.readouterr().out
        
        assert work_output != break_output
        assert "Work session" in work_output
        assert "Break" in break_output
