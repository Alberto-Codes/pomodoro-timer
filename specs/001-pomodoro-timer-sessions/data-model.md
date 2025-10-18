# Data Model: Pomodoro Timer Sessions

**Created**: October 17, 2025  
**Feature**: Pomodoro Timer Sessions (001)  
**Purpose**: Define entities, their attributes, relationships, and state machines

## Overview

This document defines the data model for the Pomodoro timer application. Since the application does not persist data (per FR-017), this model represents runtime in-memory state only.

## Entities

### SessionType (Enum)

Represents the type of timer session.

**Type**: `enum.Enum`

**Values**:
- `WORK`: 25-minute work session
- `BREAK`: 5-minute break session

**Attributes**:
```python
class SessionType(enum.Enum):
    """Types of Pomodoro timer sessions."""
    
    WORK = "work"
    BREAK = "break"
    
    @property
    def duration_seconds(self) -> int:
        """Get the duration in seconds for this session type.
        
        Returns:
            1500 for WORK (25 minutes), 300 for BREAK (5 minutes)
        """
        return 1500 if self == SessionType.WORK else 300
    
    @property
    def display_name(self) -> str:
        """Get the human-readable display name.
        
        Returns:
            "Work" or "Break"
        """
        return self.value.capitalize()
```

**Validation Rules**:
- Only two valid values (enforced by Enum)
- Duration is derived, not settable (read-only property)

---

### SessionState (Enum)

Represents the current state of a timer session.

**Type**: `enum.Enum`

**Values**:
- `IDLE`: No active session, ready to start
- `RUNNING`: Session actively counting down
- `PAUSED`: Session paused, retaining remaining time
- `COMPLETED`: Session finished (reached 00:00)

**Attributes**:
```python
class SessionState(enum.Enum):
    """States of a timer session lifecycle."""
    
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    
    @property
    def display_name(self) -> str:
        """Get the human-readable display name.
        
        Returns:
            Capitalized state name
        """
        return self.value.upper()
```

**State Transitions** (see State Machine section below)

---

### TimerSession (Class)

Represents a single Pomodoro timer session with its current state.

**Type**: Class (mutable state object)

**Attributes**:

| Attribute | Type | Description | Validation |
|-----------|------|-------------|------------|
| `session_type` | `SessionType` | Type of session (work/break) | Required, must be valid SessionType |
| `state` | `SessionState` | Current state of session | Required, must be valid SessionState |
| `remaining_seconds` | `int` | Seconds remaining in countdown | ≥ 0, ≤ `session_type.duration_seconds` |
| `start_time` | `float \| None` | Unix timestamp when session started | None if not started, >0 otherwise |
| `end_time` | `float \| None` | Unix timestamp when session should end | None if not running, >0 otherwise |

**Relationships**:
- One active `TimerSession` instance per application (singleton pattern in practice)
- No persistence relationships (no database)

**Derived Properties**:
```python
@property
def is_active(self) -> bool:
    """Check if session is running or paused."""
    return self.state in (SessionState.RUNNING, SessionState.PAUSED)

@property
def progress_percentage(self) -> float:
    """Calculate completion percentage (0.0 to 100.0)."""
    duration = self.session_type.duration_seconds
    elapsed = duration - self.remaining_seconds
    return (elapsed / duration) * 100.0 if duration > 0 else 0.0

@property
def formatted_time(self) -> str:
    """Get remaining time formatted as MM:SS."""
    minutes = self.remaining_seconds // 60
    seconds = self.remaining_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"
```

**Validation Rules**:
1. `remaining_seconds` must be non-negative
2. `remaining_seconds` cannot exceed `session_type.duration_seconds`
3. `start_time` and `end_time` must both be None or both be set when state is RUNNING
4. When state is IDLE or COMPLETED, `start_time` and `end_time` should be None
5. When state is PAUSED, only `start_time` is set (end_time cleared)

**Invariants**:
- If `state == RUNNING`, then `end_time` is set and `end_time > current_time`
- If `state == COMPLETED`, then `remaining_seconds == 0`
- If `state == IDLE`, then `remaining_seconds == session_type.duration_seconds`

---

## State Machine

### TimerSession State Transitions

```
                  ┌─────────────┐
                  │    IDLE     │
                  └──────┬──────┘
                         │
                    start_work()
                  start_break()
                         │
                         ▼
                  ┌─────────────┐
          ┌──────▶│   RUNNING   │◀─────┐
          │       └──────┬──────┘      │
          │              │              │
          │         pause()         resume()
          │              │              │
          │              ▼              │
          │       ┌─────────────┐      │
    cancel()      │   PAUSED    │──────┘
          │       └──────┬──────┘
          │              │
          │         cancel()
          │              │
          │       ┌──────▼──────┐
          │       │ COMPLETED   │
          └───────┤  (00:00)    │
                  └──────┬──────┘
                         │
                    cancel() or
                  start_work() or
                  start_break()
                         │
                         ▼
                  ┌─────────────┐
                  │    IDLE     │
                  └─────────────┘
```

### Valid State Transitions

| From State | Action | To State | Condition |
|------------|--------|----------|-----------|
| IDLE | `start_work()` | RUNNING | `session_type = WORK` |
| IDLE | `start_break()` | RUNNING | `session_type = BREAK` |
| RUNNING | `pause()` | PAUSED | None |
| RUNNING | `cancel()` | IDLE | None |
| RUNNING | _timer_reaches_zero_ | COMPLETED | `remaining_seconds == 0` |
| PAUSED | `resume()` | RUNNING | None |
| PAUSED | `cancel()` | IDLE | None |
| COMPLETED | `cancel()` | IDLE | None |
| COMPLETED | `start_work()` | RUNNING | `session_type = WORK` |
| COMPLETED | `start_break()` | RUNNING | `session_type = BREAK` |

### Invalid State Transitions (Raise Exceptions)

| From State | Action | Exception | Reason |
|------------|--------|-----------|--------|
| RUNNING | `start_work()` | `SessionAlreadyActive` | Cannot start new session while one is active (FR-011) |
| RUNNING | `start_break()` | `SessionAlreadyActive` | Cannot start new session while one is active (FR-011) |
| RUNNING | `resume()` | `InvalidStateTransition` | Cannot resume already running session |
| PAUSED | `start_work()` | `SessionAlreadyActive` | Must cancel paused session before starting new one |
| PAUSED | `start_break()` | `SessionAlreadyActive` | Must cancel paused session before starting new one |
| PAUSED | `pause()` | `InvalidStateTransition` | Cannot pause already paused session |
| IDLE | `pause()` | `InvalidStateTransition` | Cannot pause when no session active |
| IDLE | `resume()` | `InvalidStateTransition` | Cannot resume when no session active |
| IDLE | `cancel()` | `InvalidStateTransition` | Cannot cancel when no session active (no-op allowed) |
| COMPLETED | `pause()` | `InvalidStateTransition` | Cannot pause completed session |
| COMPLETED | `resume()` | `InvalidStateTransition` | Cannot resume completed session |

---

## Behavioral Methods

### TimerSession Methods

```python
class TimerSession:
    """Represents a Pomodoro timer session with state management."""
    
    def start_work(self) -> None:
        """Start a new 25-minute work session.
        
        Raises:
            SessionAlreadyActive: If session already running or paused
        """
        # Validate state is IDLE or COMPLETED
        # Set session_type = WORK
        # Set state = RUNNING
        # Set start_time = current timestamp
        # Set end_time = start_time + 1500 seconds
        # Set remaining_seconds = 1500
    
    def start_break(self) -> None:
        """Start a new 5-minute break session.
        
        Raises:
            SessionAlreadyActive: If session already running or paused
        """
        # Similar to start_work but with BREAK type and 300 seconds
    
    def pause(self) -> None:
        """Pause the currently running session.
        
        Raises:
            InvalidStateTransition: If state is not RUNNING
        """
        # Validate state is RUNNING
        # Calculate remaining_seconds from current time vs end_time
        # Set state = PAUSED
        # Clear end_time (keep start_time for resume)
    
    def resume(self) -> None:
        """Resume a paused session.
        
        Raises:
            InvalidStateTransition: If state is not PAUSED
        """
        # Validate state is PAUSED
        # Set state = RUNNING
        # Set end_time = current timestamp + remaining_seconds
    
    def cancel(self) -> None:
        """Cancel the current session and return to idle.
        
        Raises:
            InvalidStateTransition: If state is already IDLE (optional)
        """
        # Set state = IDLE
        # Reset all timestamps to None
        # Reset remaining_seconds to 0 (will be set on next start)
    
    def tick(self) -> None:
        """Update remaining time based on current time.
        
        Should be called periodically (e.g., every 0.1s) when state is RUNNING.
        Automatically transitions to COMPLETED when time reaches zero.
        """
        # If state != RUNNING, return early
        # Calculate remaining = end_time - current_time
        # If remaining <= 0:
        #     Set remaining_seconds = 0
        #     Set state = COMPLETED
        #     Clear timestamps
        #     Trigger notification
        # Else:
        #     Set remaining_seconds = remaining
```

---

## Example Usage

```python
# Create new idle session
session = TimerSession()
assert session.state == SessionState.IDLE

# Start work session
session.start_work()
assert session.state == SessionState.RUNNING
assert session.session_type == SessionType.WORK
assert session.remaining_seconds == 1500

# Pause after some time
time.sleep(10)
session.tick()  # Update remaining time
session.pause()
assert session.state == SessionState.PAUSED
assert session.remaining_seconds < 1500  # Some time elapsed

# Resume
session.resume()
assert session.state == SessionState.RUNNING

# Cancel
session.cancel()
assert session.state == SessionState.IDLE
```

---

## Data Model Alignment with Requirements

| Requirement | Model Element | How Satisfied |
|-------------|---------------|---------------|
| FR-001 | `SessionType.WORK` with `duration_seconds = 1500` | 25-minute work sessions |
| FR-002 | `SessionType.BREAK` with `duration_seconds = 300` | 5-minute break sessions |
| FR-003 | `TimerSession.formatted_time` property | MM:SS format |
| FR-006 | `TimerSession.start_work()` from IDLE state | Start work from idle |
| FR-007 | `TimerSession.start_break()` from IDLE or COMPLETED | Start break anytime |
| FR-008 | `TimerSession.pause()` method | Pause active timer |
| FR-009 | `TimerSession.resume()` method | Resume paused timer |
| FR-010 | `TimerSession.cancel()` method | Cancel active/paused |
| FR-011 | State validation in `start_*()` methods | Prevent concurrent sessions |
| FR-012 | `TimerSession.session_type` attribute | Display session type |
| FR-013 | `TimerSession.state` attribute | Display session state |
| FR-016 | State machine: RUNNING → COMPLETED (stays) | Completed state persists |
| FR-017 | No persistence fields/methods | No cross-restart state |
| FR-018 | No auto-transition logic in state machine | Manual transitions only |

---

## Implementation Notes

1. **Thread Safety**: Not required. Application runs in single-threaded asyncio loop.
2. **Serialization**: Not required. No persistence per FR-017.
3. **Validation**: Use Python properties with setters to enforce invariants.
4. **Type Hints**: All attributes and methods must have complete type hints for `ty` checking.
5. **Testing**: State machine transitions are critical - test all valid and invalid paths.
