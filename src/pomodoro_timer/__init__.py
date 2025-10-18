"""Pomodoro timer application."""

import asyncio
import sys

from pomodoro_timer.cli.commands import create_parser, run_command


def main() -> None:
    """Run the pomodoro timer application."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        exit_code = asyncio.run(run_command(args))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        sys.exit(3)
