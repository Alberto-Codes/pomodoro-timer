# Research: Pomodoro Timer Sessions

**Created**: October 17, 2025  
**Feature**: Pomodoro Timer Sessions (001)  
**Purpose**: Technical research to resolve implementation unknowns and establish best practices

## Overview

This document consolidates research findings for implementing a Python CLI-based Pomodoro timer with accurate time tracking, responsive user controls, and effective notifications.

## Research Areas

### 1. Python CLI Timer Implementation

**Decision**: Use `asyncio` event loop with `asyncio.sleep()` for timer implementation

**Rationale**:
- Provides accurate time tracking without blocking
- Enables responsive user input handling during countdown
- Native Python 3.12+ stdlib - no external dependencies
- Clean async/await syntax for timer logic
- Built-in task cancellation for pause/stop operations

**Alternatives Considered**:
- `threading.Timer`: Rejected - harder to manage state, less accurate for sub-second timing
- `time.sleep()` in loop: Rejected - blocks execution, can't handle concurrent input
- Third-party frameworks (e.g., `prompt_toolkit`): Rejected - violates simplicity principle, adds dependency

**Implementation Pattern**:
```python
async def timer_loop(duration_seconds: int) -> None:
    """Run timer countdown with 1-second precision."""
    end_time = time.time() + duration_seconds
    while time.time() < end_time:
        remaining = int(end_time - time.time())
        # Update display
        await asyncio.sleep(0.1)  # Check 10x/sec for responsiveness
```

### 2. Time Tracking Accuracy

**Decision**: Use `time.time()` (monotonic system time) for countdown calculations

**Rationale**:
- Measures elapsed real time independent of display refresh rate
- Immune to minor system time adjustments (< 1 hour)
- Achieves <1 second accuracy requirement (SC-001, SC-002)
- Simple arithmetic: `remaining = end_time - current_time`

**Alternatives Considered**:
- `time.monotonic()`: Rejected - `time.time()` sufficient for this use case, monotonic overkill
- Tick counting (`sleep(1)` per second): Rejected - drift accumulates, less accurate
- External time service: Rejected - unnecessary complexity, offline capability lost

**Accuracy Strategy**:
- Calculate target end time once at session start
- Each loop iteration computes remaining time from current time
- Display rounds to nearest second
- Notifications trigger when `remaining <= 0`

### 3. Terminal Display Formatting

**Decision**: Use ANSI escape codes for in-place display updates with `\r` (carriage return)

**Rationale**:
- Cross-platform support (Windows 10+, Linux, macOS)
- No external dependencies
- Smooth display without terminal scroll
- Simple implementation via `sys.stdout.write()` and `flush()`

**Alternatives Considered**:
- `curses` library: Rejected - overkill for simple display, platform compatibility issues on Windows
- `rich` library: Rejected - external dependency, violates simplicity
- Print new line each second: Rejected - clutters terminal, poor UX

**Implementation Pattern**:
```python
def update_display(minutes: int, seconds: int, state: str) -> None:
    """Update timer display in-place."""
    display = f"\r{state}: {minutes:02d}:{seconds:02d}"
    sys.stdout.write(display)
    sys.stdout.flush()
```

**Display Format**: `STATE: MM:SS` where STATE is "WORK", "BREAK", "PAUSED", or "COMPLETED"

### 4. Audio Notifications

**Decision**: Use `\a` (ASCII bell character) for cross-platform audio notification

**Rationale**:
- Built into terminal emulators (no dependencies)
- Works on Windows, Linux, macOS
- Simple one-line implementation
- User can configure terminal to use custom sound
- Meets FR-004 and FR-005 requirements

**Alternatives Considered**:
- `winsound` (Windows): Rejected - platform-specific, breaks cross-platform goal
- `playsound` library: Rejected - external dependency, overkill
- System notification APIs: Rejected - complexity, requires platform-specific code

**Implementation Pattern**:
```python
def play_notification_sound() -> None:
    """Play terminal bell sound."""
    print("\a", end="", flush=True)
```

**Enhancement Path**: Future enhancement could detect terminal capabilities and fall back gracefully if bell disabled.

### 5. Timer State Management

**Decision**: Use Python `enum.Enum` for state machine with explicit state transitions

**Rationale**:
- Type-safe state representation (catches invalid states at type-check time)
- Self-documenting code
- Explicit transition validation prevents invalid state changes
- Aligns with FR-013 requirement (display current state)

**State Machine Design**:
```
States: IDLE, RUNNING, PAUSED, COMPLETED

Transitions:
- IDLE → RUNNING: start_work() or start_break()
- RUNNING → PAUSED: pause()
- RUNNING → COMPLETED: timer reaches 0:00
- PAUSED → RUNNING: resume()
- PAUSED → IDLE: cancel()
- RUNNING → IDLE: cancel()
- COMPLETED → IDLE: cancel() or timeout
- COMPLETED → RUNNING: start_work() or start_break()
```

**Alternatives Considered**:
- String-based states: Rejected - no type safety, typo-prone
- Boolean flags (`is_running`, `is_paused`): Rejected - complex logic, mutually exclusive states unclear
- State pattern (GoF): Rejected - premature abstraction for 4 states

### 6. CLI Command Interface

**Decision**: Use Python's `argparse` for command parsing, defer to future enhancement for interactive mode

**Rationale**:
- Stdlib solution (no dependencies)
- Standard CLI argument patterns
- Extensible for future subcommands
- Type-safe with proper help text

**Initial Command Set**:
```
pomodoro-timer start [work|break]  # Start session
pomodoro-timer pause               # Pause active session
pomodoro-timer resume              # Resume paused session
pomodoro-timer cancel              # Cancel active/paused session
pomodoro-timer status              # Show current timer state
```

**Alternatives Considered**:
- `click` library: Rejected - external dependency, argparse sufficient for MVP
- Interactive TUI (single long-running process): Deferred - more complex, can add later if needed
- No CLI args (always start work session): Rejected - doesn't satisfy FR-006, FR-007

**Future Enhancement**: Interactive mode where app runs continuously and accepts keyboard commands (s=start, p=pause, r=resume, c=cancel). This would require `asyncio` for concurrent input handling.

### 7. Testing Strategy

**Decision**: Pytest with `pytest-asyncio` for async test support, `freezegun` for time mocking

**Rationale**:
- `pytest-asyncio`: Native support for testing async functions
- `freezegun`: Mock time progression without actual delays (fast tests)
- Matches project's existing pytest setup
- Enables TDD workflow per Constitution Principle I

**Test Categories**:
1. **Unit Tests**:
   - Session state transitions (all valid/invalid paths)
   - Timer calculations (edge cases: 0 seconds, negative, overflow)
   - Display formatting (MM:SS padding, state labels)
   - Notification triggering

2. **Integration Tests**:
   - Full user story workflows (acceptance scenarios)
   - End-to-end timer countdown with mocked time
   - Command sequence validation (start→pause→resume→complete)

**Time Mocking Pattern**:
```python
from freezegun import freeze_time
import time

@freeze_time("2025-10-17 10:00:00")
def test_timer_countdown():
    # Start timer
    # Advance time
    # Assert remaining time
```

**External Dependencies Needed**:
- `pytest-asyncio`: For async test support
- `freezegun`: For time mocking

### 8. Error Handling Patterns

**Decision**: Raise custom exceptions for invalid state transitions, graceful degradation for notifications

**Rationale**:
- Clear error messages improve debugging
- Prevents silent failures
- Type-safe error handling with specific exception types
- Graceful degradation for non-critical features (audio)

**Exception Hierarchy**:
```python
class TimerError(Exception):
    """Base exception for timer errors."""

class InvalidStateTransition(TimerError):
    """Attempted invalid state transition."""

class SessionAlreadyActive(TimerError):
    """Attempted to start session while one is active."""
```

**Notification Fallback**:
- If terminal bell fails, log warning but continue
- Visual notification always shown (critical path)
- Audio is enhancement, not blocker

## Dependencies Summary

### Production Dependencies
- **None** - Using Python 3.12+ stdlib only (`asyncio`, `time`, `enum`, `sys`, `argparse`)

### Development Dependencies (to add via `uv add --dev`)
- `pytest-asyncio` - Async test support
- `freezegun` - Time mocking for tests

### Already Configured
- `pytest` - Test runner
- `pytest-xdist` - Parallel test execution
- `ruff` - Linting and formatting
- `ty` - Type checking

## Performance Considerations

### Timer Accuracy
- **Target**: <1 second deviation over 25-minute session
- **Approach**: Calculate from fixed end time, not accumulated sleep durations
- **Validation**: Integration tests with mocked time verify accuracy

### Display Refresh
- **Target**: 1 Hz (once per second) per SC-004
- **Approach**: Update every loop iteration (0.1s sleep = 10 Hz actual, display shows seconds)
- **Optimization**: Only redraw when displayed second changes

### Response Time
- **Target**: <500ms for user commands per SC-007
- **Approach**: Check for commands every 0.1s in timer loop
- **Implementation**: Non-blocking async input handling

## Open Questions & Future Enhancements

### Resolved (No Action Needed for MVP)
- ✅ Session persistence: Clarified as not in scope (FR-017)
- ✅ Long breaks: Clarified as not in scope
- ✅ Auto-transitions: Clarified as manual only (FR-018)

### Deferred to Future Iterations
- **Interactive TUI mode**: Single long-running process with keyboard commands (post-MVP)
- **Session history/stats**: Track completed pomodoros (out of scope per spec)
- **Custom durations**: Configure work/break times (out of scope per spec)
- **Sound customization**: Custom audio files instead of terminal bell (enhancement)

## Implementation Priorities (Aligned with User Stories)

### P1 - Start and Complete Work Session (MVP Blocker)
- Session model with state machine
- Timer engine with asyncio loop
- Display formatting (MM:SS)
- Visual notification on completion
- Audio notification (terminal bell)
- Basic CLI (start command)

### P2 - Take Short Break (Core Cycle Complete)
- Break session type
- Session type differentiation in display
- Different notification messages for work vs. break

### P3 - Pause and Resume Sessions
- Pause state and transitions
- Resume functionality
- Paused state display

### P3 - Cancel Active Session
- Cancel command
- State reset to idle
- Cleanup logic

## Conclusion

This research establishes a clear technical foundation using Python stdlib components (asyncio, time, enum, argparse) with minimal external dependencies (pytest-asyncio, freezegun for testing only). The design prioritizes simplicity, accuracy, and cross-platform compatibility while maintaining strict adherence to the project constitution's principles.

All technical unknowns from the plan's Technical Context have been resolved with justified decisions and clear implementation patterns.
