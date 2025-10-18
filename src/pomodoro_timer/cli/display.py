"""Terminal display formatting for Pomodoro timer."""

import sys


def format_time(seconds: int) -> str:
    """Convert seconds to MM:SS string with zero-padding.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string in MM:SS format
    """
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def display_timer(session_type: str, time_str: str, state: str) -> None:
    """Display timer in terminal with in-place updates.

    Args:
        session_type: Type of session (e.g., "Work", "Break")
        time_str: Formatted time string (MM:SS)
        state: Current state (e.g., "RUNNING", "PAUSED")
    """
    # Use \r to return cursor to start of line for in-place update
    sys.stdout.write(f"\r{state}: {session_type} - {time_str}")
    sys.stdout.flush()


def clear_line() -> None:
    """Clear the current line in terminal."""
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()
