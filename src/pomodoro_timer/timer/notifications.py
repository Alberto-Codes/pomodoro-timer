"""Notification handlers for timer completion."""

import sys

from pomodoro_timer.models.types import SessionType


def notify_completion(session_type: SessionType) -> None:
    """Notify user that a session has completed.

    Args:
        session_type: Type of session that completed (WORK or BREAK)
    """
    # Visual message
    if session_type == SessionType.WORK:
        message = "\n✓ Work session complete! Time for a break."
    else:
        message = "\n✓ Break complete! Ready to focus again."

    print(message)

    # Audio notification (best-effort, no error if terminal doesn't support)
    try:
        sys.stdout.write("\a")  # Terminal bell
        sys.stdout.flush()
    except Exception:
        # Silently ignore if audio not supported
        pass
