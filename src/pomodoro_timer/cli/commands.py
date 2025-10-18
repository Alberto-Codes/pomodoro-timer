"""CLI command handlers for Pomodoro timer."""

import argparse
import sys

from pomodoro_timer.models.session import TimerSession
from pomodoro_timer.timer.engine import TimerEngine


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="pomodoro-timer",
        description="CLI Pomodoro timer with 25-minute work sessions and 5-minute breaks",
    )

    # Add --ui flag for launching web interface
    parser.add_argument(
        "--ui",
        action="store_true",
        help="Launch web-based UI instead of CLI",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start a timer session")
    start_parser.add_argument(
        "session_type",
        choices=["work", "break"],
        help="Type of session to start",
    )

    # Pause command
    subparsers.add_parser("pause", help="Pause the active timer")

    # Resume command
    subparsers.add_parser("resume", help="Resume a paused timer")

    # Cancel command
    subparsers.add_parser("cancel", help="Cancel the active timer")

    # Status command
    subparsers.add_parser("status", help="Show current timer status")

    return parser


async def handle_start(session: TimerSession, session_type: str) -> int:
    """Handle start command.

    Args:
        session: Timer session instance
        session_type: Type of session ("work" or "break")

    Returns:
        Exit code (0=success, 2=invalid state)
    """
    engine = TimerEngine(session)

    try:
        if session_type == "work":
            await engine.start_work()
        else:
            await engine.start_break()
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


def handle_status(session: TimerSession) -> int:
    """Handle status command.

    Args:
        session: Timer session instance

    Returns:
        Exit code (0=success)
    """
    print(f"State: {session.state.display_name}")

    if session.session_type:
        print(f"Session Type: {session.session_type.display_name}")
        print(f"Remaining Time: {session.formatted_time}")
    else:
        print("No active session")

    return 0


async def run_command(args: argparse.Namespace) -> int:
    """Execute the requested command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code
    """
    # Global session instance (in real app, might be persisted)
    session = TimerSession()

    if args.command == "start":
        return await handle_start(session, args.session_type)
    elif args.command == "status":
        return handle_status(session)
    elif args.command == "pause":
        return handle_pause(session)
    elif args.command == "resume":
        return await handle_resume(session)
    elif args.command == "cancel":
        return handle_cancel(session)
    else:
        print("Error: No command specified. Use --help for usage information.", file=sys.stderr)
        return 1


def handle_pause(session: TimerSession) -> int:
    """Handle pause command.

    Args:
        session: Timer session instance

    Returns:
        Exit code (0=success, 2=invalid state)
    """
    try:
        session.pause()
        print(f"Timer paused at {session.formatted_time}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


async def handle_resume(session: TimerSession) -> int:
    """Handle resume command.

    Args:
        session: Timer session instance

    Returns:
        Exit code (0=success, 2=invalid state)
    """
    try:
        engine = TimerEngine(session)
        await engine.resume()
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


def handle_cancel(session: TimerSession) -> int:
    """Handle cancel command.

    Args:
        session: Timer session instance

    Returns:
        Exit code (0=success)
    """
    session.cancel()
    print("Timer canceled")
    return 0
