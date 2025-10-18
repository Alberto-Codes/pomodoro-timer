"""Unit tests for CLI display functions."""

import sys
from io import StringIO

import pytest

from pomodoro_timer.cli.display import clear_line, display_timer, format_time


class TestFormatTime:
    """Tests for format_time() function."""

    def test_format_time_zero_seconds(self):
        """Test formatting zero seconds."""
        assert format_time(0) == "00:00"

    def test_format_time_under_one_minute(self):
        """Test formatting seconds under one minute."""
        assert format_time(45) == "00:45"

    def test_format_time_exactly_one_minute(self):
        """Test formatting exactly one minute."""
        assert format_time(60) == "01:00"

    def test_format_time_multiple_minutes(self):
        """Test formatting multiple minutes."""
        assert format_time(325) == "05:25"

    def test_format_time_work_session_duration(self):
        """Test formatting 25-minute work session."""
        assert format_time(1500) == "25:00"

    def test_format_time_break_session_duration(self):
        """Test formatting 5-minute break session."""
        assert format_time(300) == "05:00"

    def test_format_time_with_zero_padding(self):
        """Test that single digits are zero-padded."""
        assert format_time(65) == "01:05"
        assert format_time(9) == "00:09"


class TestDisplayTimer:
    """Tests for display_timer() function."""

    def test_display_timer_work_session(self, capsys):
        """Test displaying a work session timer."""
        display_timer("Work", "25:00", "RUNNING")
        
        captured = capsys.readouterr()
        assert "RUNNING: Work - 25:00" in captured.out

    def test_display_timer_break_session(self, capsys):
        """Test displaying a break session timer."""
        display_timer("Break", "05:00", "RUNNING")
        
        captured = capsys.readouterr()
        assert "RUNNING: Break - 05:00" in captured.out

    def test_display_timer_paused_state(self, capsys):
        """Test displaying a paused timer."""
        display_timer("Work", "15:30", "PAUSED")
        
        captured = capsys.readouterr()
        assert "PAUSED: Work - 15:30" in captured.out

    def test_display_timer_uses_carriage_return(self, monkeypatch):
        """Test that display_timer uses carriage return for in-place updates."""
        output = StringIO()
        monkeypatch.setattr(sys, "stdout", output)
        
        display_timer("Work", "10:00", "RUNNING")
        
        result = output.getvalue()
        assert result.startswith("\r")
        assert "RUNNING: Work - 10:00" in result

    def test_display_timer_flushes_output(self, monkeypatch):
        """Test that display_timer flushes stdout."""
        flush_called = False
        original_write = sys.stdout.write
        
        def mock_write(text):
            original_write(text)
        
        def mock_flush():
            nonlocal flush_called
            flush_called = True
        
        monkeypatch.setattr(sys.stdout, "write", mock_write)
        monkeypatch.setattr(sys.stdout, "flush", mock_flush)
        
        display_timer("Work", "10:00", "RUNNING")
        
        assert flush_called


class TestClearLine:
    """Tests for clear_line() function."""

    def test_clear_line_writes_spaces(self, monkeypatch):
        """Test that clear_line writes spaces to clear the line."""
        output = StringIO()
        monkeypatch.setattr(sys, "stdout", output)
        
        clear_line()
        
        result = output.getvalue()
        assert "\r" in result
        assert " " * 80 in result

    def test_clear_line_returns_to_start(self, monkeypatch):
        """Test that clear_line returns cursor to line start."""
        output = StringIO()
        monkeypatch.setattr(sys, "stdout", output)
        
        clear_line()
        
        result = output.getvalue()
        # Should start and end with carriage return
        assert result.startswith("\r")
        assert result.endswith("\r")

    def test_clear_line_flushes_output(self, monkeypatch):
        """Test that clear_line flushes stdout."""
        flush_called = False
        original_write = sys.stdout.write
        
        def mock_write(text):
            original_write(text)
        
        def mock_flush():
            nonlocal flush_called
            flush_called = True
        
        monkeypatch.setattr(sys.stdout, "write", mock_write)
        monkeypatch.setattr(sys.stdout, "flush", mock_flush)
        
        clear_line()
        
        assert flush_called
