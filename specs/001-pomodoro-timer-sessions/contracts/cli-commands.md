# CLI Command Contracts

**Created**: October 17, 2025  
**Feature**: Pomodoro Timer Sessions (001)  
**Type**: Command-Line Interface Specification

## Overview

This document defines the command-line interface contracts for the Pomodoro timer application. Unlike REST APIs, CLI commands are specified in terms of command syntax, arguments, options, exit codes, and output formats.

## General Conventions

### Exit Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 0 | Success | Command completed successfully |
| 1 | General error | Invalid usage, argument error |
| 2 | Invalid state | Attempted invalid state transition |
| 3 | Interrupted | User pressed Ctrl+C during timer |

### Output Format

- **Standard Output (stdout)**: Command results, timer display, success messages
- **Standard Error (stderr)**: Error messages, warnings
- **Display Updates**: Use `\r` (carriage return) for in-place timer updates

### Time Format

All time displays use `MM:SS` format with zero-padding:
- `25:00` - 25 minutes remaining
- `05:00` - 5 minutes remaining
- `00:30` - 30 seconds remaining
- `00:00` - Completed

---

## Commands

### `pomodoro-timer` (Entry Point)

**Syntax**: `pomodoro-timer`

**Description**: Display help and usage information (default behavior when no subcommand)

**Output**:
```
Pomodoro Timer - Focus on what matters

Usage: pomodoro-timer <command> [options]

Commands:
  start <type>    Start a new timer session (work|break)
  pause           Pause the active timer
  resume          Resume a paused timer
  cancel          Cancel the active timer
  status          Show current timer status

Run 'pomodoro-timer <command> --help' for command-specific help.
```

**Exit Code**: 0

---

### `start` Command

**Syntax**: `pomodoro-timer start <type>`

**Description**: Start a new Pomodoro timer session

**Arguments**:

| Argument | Type | Required | Valid Values | Description |
|----------|------|----------|--------------|-------------|
| `type` | String | Yes | `work`, `break` | Type of session to start |

**Options**: None

**Preconditions**:
- No session currently RUNNING or PAUSED (enforces FR-011)

**Success Output** (to stdout):
```
Starting work session (25:00)...

WORK: 25:00
```

_Then timer begins counting down with in-place updates:_
```
WORK: 24:59
WORK: 24:58
...
```

**Completion Output** (when timer reaches 00:00):
```
WORK: 00:00

🔔 Work session complete! Time for a break.
```

_Plus terminal bell character (`\a`)_

**Error Conditions**:

| Error | Output (stderr) | Exit Code |
|-------|-----------------|-----------|
| Invalid type | `Error: Invalid session type 'xyz'. Use 'work' or 'break'.` | 1 |
| Session already active | `Error: A session is already running. Use 'pause' or 'cancel' first.` | 2 |
| Missing argument | `Error: Missing required argument 'type'.\nUsage: pomodoro-timer start <work\|break>` | 1 |

**Examples**:
```bash
# Start work session
$ pomodoro-timer start work
Starting work session (25:00)...
WORK: 25:00

# Start break session
$ pomodoro-timer start break
Starting break session (05:00)...
BREAK: 05:00

# Error: session already active
$ pomodoro-timer start work
Error: A session is already running. Use 'pause' or 'cancel' first.
```

---

### `pause` Command

**Syntax**: `pomodoro-timer pause`

**Description**: Pause the currently running timer session

**Arguments**: None

**Options**: None

**Preconditions**:
- Session state must be RUNNING

**Success Output** (to stdout):
```
WORK: 18:42 (PAUSED)

Timer paused. Use 'resume' to continue or 'cancel' to stop.
```

**Error Conditions**:

| Error | Output (stderr) | Exit Code |
|-------|-----------------|-----------|
| No active session | `Error: No active session to pause.` | 2 |
| Already paused | `Error: Timer is already paused.` | 2 |
| Session completed | `Error: Cannot pause a completed session.` | 2 |

**Examples**:
```bash
# Pause running timer
$ pomodoro-timer pause
WORK: 18:42 (PAUSED)

Timer paused. Use 'resume' to continue or 'cancel' to stop.

# Error: no active session
$ pomodoro-timer pause
Error: No active session to pause.
```

---

### `resume` Command

**Syntax**: `pomodoro-timer resume`

**Description**: Resume a paused timer session

**Arguments**: None

**Options**: None

**Preconditions**:
- Session state must be PAUSED

**Success Output** (to stdout):
```
Resuming work session...

WORK: 18:42
```

_Timer continues counting down from paused time_

**Error Conditions**:

| Error | Output (stderr) | Exit Code |
|-------|-----------------|-----------|
| No paused session | `Error: No paused session to resume.` | 2 |
| Already running | `Error: Timer is already running.` | 2 |

**Examples**:
```bash
# Resume paused timer
$ pomodoro-timer resume
Resuming work session...
WORK: 18:42

# Error: not paused
$ pomodoro-timer resume
Error: No paused session to resume.
```

---

### `cancel` Command

**Syntax**: `pomodoro-timer cancel`

**Description**: Cancel the active or paused timer and return to idle state

**Arguments**: None

**Options**: None

**Preconditions**:
- Session state must be RUNNING, PAUSED, or COMPLETED

**Success Output** (to stdout):
```
Timer cancelled.
```

**Error Conditions**:

| Error | Output (stderr) | Exit Code |
|-------|-----------------|-----------|
| No session to cancel | `Error: No active session to cancel.` | 2 |

_Note: Can be made more lenient to return exit code 0 when idle (no-op)_

**Examples**:
```bash
# Cancel running timer
$ pomodoro-timer cancel
Timer cancelled.

# Cancel after completion (resets to idle)
$ pomodoro-timer cancel
Timer cancelled.
```

---

### `status` Command

**Syntax**: `pomodoro-timer status`

**Description**: Display current timer status without starting interactive display

**Arguments**: None

**Options**: None

**Preconditions**: None (works in any state)

**Success Output** (varies by state):

**When IDLE**:
```
Status: Idle
No active timer session.
```

**When RUNNING**:
```
Status: Running
Type: Work
Time Remaining: 18:42
Progress: 25.3%
```

**When PAUSED**:
```
Status: Paused
Type: Break
Time Remaining: 03:15
Progress: 35.0%
```

**When COMPLETED**:
```
Status: Completed
Type: Work
Session finished at 00:00
```

**Error Conditions**: None

**Exit Code**: Always 0

**Examples**:
```bash
# Check status while idle
$ pomodoro-timer status
Status: Idle
No active timer session.

# Check status during work session
$ pomodoro-timer status
Status: Running
Type: Work
Time Remaining: 18:42
Progress: 25.3%
```

---

## Implementation Notes

### Command Parsing

Use Python's `argparse` module:

```python
import argparse

parser = argparse.ArgumentParser(
    prog='pomodoro-timer',
    description='Pomodoro Timer - Focus on what matters'
)
subparsers = parser.add_subparsers(dest='command', help='Available commands')

# start command
start_parser = subparsers.add_parser('start', help='Start a timer session')
start_parser.add_argument('type', choices=['work', 'break'], help='Session type')

# pause command
subparsers.add_parser('pause', help='Pause the active timer')

# resume command
subparsers.add_parser('resume', help='Resume a paused timer')

# cancel command
subparsers.add_parser('cancel', help='Cancel the active timer')

# status command
subparsers.add_parser('status', help='Show timer status')
```

### Display Updates

For `start` command, use async loop with in-place updates:

```python
import sys
import asyncio

async def display_timer(session: TimerSession) -> None:
    """Display timer countdown with in-place updates."""
    last_displayed = -1
    
    while session.state == SessionState.RUNNING:
        session.tick()
        
        if session.remaining_seconds != last_displayed:
            formatted = session.formatted_time
            display = f"\r{session.session_type.display_name.upper()}: {formatted}"
            sys.stdout.write(display)
            sys.stdout.flush()
            last_displayed = session.remaining_seconds
        
        await asyncio.sleep(0.1)  # Check 10x per second
    
    # Final display at completion
    if session.state == SessionState.COMPLETED:
        print()  # New line after timer display
        print(f"\n🔔 {session.session_type.display_name} session complete!", flush=True)
        print("\a", end="", flush=True)  # Terminal bell
```

### Error Handling

```python
class CLIError(Exception):
    """Base exception for CLI errors."""
    exit_code: int = 1

class InvalidStateError(CLIError):
    """Invalid state transition attempted."""
    exit_code: int = 2

class InterruptedError(CLIError):
    """User interrupted operation."""
    exit_code: int = 3

def handle_error(error: Exception) -> int:
    """Handle CLI error and return appropriate exit code."""
    if isinstance(error, CLIError):
        print(f"Error: {error}", file=sys.stderr)
        return error.exit_code
    print(f"Unexpected error: {error}", file=sys.stderr)
    return 1
```

---

## Contract Alignment with Requirements

| Requirement | Contract Element | How Satisfied |
|-------------|------------------|---------------|
| FR-001 | `start work` command with 25:00 display | 25-minute work sessions |
| FR-002 | `start break` command with 05:00 display | 5-minute break sessions |
| FR-003 | `MM:SS` format in all time displays | Display format specification |
| FR-004 | Completion message + `\a` for work | Visual + audio notification |
| FR-005 | Completion message + `\a` for break | Visual + audio notification |
| FR-006 | `start work` command from idle | Start work from idle |
| FR-007 | `start break` command from idle/completed | Start break anytime |
| FR-008 | `pause` command | Pause active timer |
| FR-009 | `resume` command | Resume paused timer |
| FR-010 | `cancel` command | Cancel active/paused |
| FR-011 | Error when starting with active session | Prevent concurrent sessions |
| FR-012 | Session type in display (`WORK`/`BREAK`) | Display session type |
| FR-013 | State shown in output (Running/Paused/etc) | Display session state |
| FR-015 | Different completion messages | Distinguishable notifications |
| FR-016 | Completed state shown until next action | Status command shows completed |
| FR-018 | No auto-transition to break | Manual commands only |

---

## Testing Strategy

Each command should have:
1. **Happy path test**: Valid usage succeeds
2. **Invalid argument test**: Wrong args produce error
3. **Invalid state test**: Command in wrong state produces error
4. **Output validation test**: stdout/stderr match specification
5. **Exit code test**: Correct exit codes returned
