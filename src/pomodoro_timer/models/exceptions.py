"""Custom exceptions for Pomodoro timer."""


class TimerError(Exception):
    """Base exception for timer-related errors."""

    pass


class InvalidStateTransition(TimerError):
    """Raised when attempting an invalid state transition."""

    pass


class SessionAlreadyActive(TimerError):
    """Raised when attempting to start a session while one is already active."""

    pass
