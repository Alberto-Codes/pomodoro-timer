"""Unit tests for main application entry point."""

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pomodoro_timer import main


class TestMain:
    """Tests for main() function."""

    @patch("pomodoro_timer.create_parser")
    @patch("pomodoro_timer.asyncio.run")
    @patch("pomodoro_timer.run_command")
    def test_main_calls_parser_and_runs_command(
        self, mock_run_command, mock_asyncio_run, mock_create_parser
    ):
        """Test that main creates parser, parses args, and runs command."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_create_parser.return_value = mock_parser
        mock_asyncio_run.return_value = 0
        
        # Override sys.exit to prevent actual exit
        with patch("sys.exit") as mock_exit:
            main()
            
            mock_create_parser.assert_called_once()
            mock_parser.parse_args.assert_called_once()
            mock_asyncio_run.assert_called_once()
            mock_exit.assert_called_once_with(0)

    @patch("pomodoro_timer.create_parser")
    @patch("pomodoro_timer.asyncio.run")
    @patch("pomodoro_timer.run_command")
    def test_main_exits_with_command_result(
        self, mock_run_command, mock_asyncio_run, mock_create_parser
    ):
        """Test that main exits with the result code from run_command."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_create_parser.return_value = mock_parser
        mock_asyncio_run.return_value = 2  # Error code
        
        with patch("sys.exit") as mock_exit:
            main()
            
            mock_exit.assert_called_once_with(2)

    @patch("pomodoro_timer.create_parser")
    @patch("pomodoro_timer.asyncio.run")
    def test_main_handles_keyboard_interrupt(self, mock_asyncio_run, mock_create_parser):
        """Test that main handles KeyboardInterrupt gracefully."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_create_parser.return_value = mock_parser
        mock_asyncio_run.side_effect = KeyboardInterrupt()
        
        with patch("sys.exit") as mock_exit:
            with patch("sys.stderr") as mock_stderr:
                main()
                
                # Should print interrupt message
                assert any("Interrupted" in str(call) for call in mock_stderr.write.call_args_list 
                          or "Interrupted" in str(call) for call in getattr(mock_stderr, 'mock_calls', []))
                
                # Should exit with code 3
                mock_exit.assert_called_once_with(3)

    @patch("pomodoro_timer.create_parser")
    @patch("pomodoro_timer.asyncio.run")
    def test_main_prints_interrupt_message_to_stderr(
        self, mock_asyncio_run, mock_create_parser, capsys
    ):
        """Test that KeyboardInterrupt message goes to stderr."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_create_parser.return_value = mock_parser
        mock_asyncio_run.side_effect = KeyboardInterrupt()
        
        with patch("sys.exit"):
            main()
            
            captured = capsys.readouterr()
            assert "Interrupted" in captured.err or "Interrupted" in captured.out
