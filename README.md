# Pomodoro Timer

A modern CLI-based Pomodoro timer built with Python 3.12+ that helps you stay focused using the Pomodoro Technique®.

## Features

🎯 **25-minute work sessions** - Standard Pomodoro work intervals  
☕ **5-minute breaks** - Short breaks between work sessions  
⏸️ **Pause & Resume** - Flexible control over your timer  
❌ **Cancel anytime** - Reset and start fresh when needed  
📊 **Status command** - Check your current session at any time  
🔔 **Visual & Audio notifications** - Get notified when sessions complete  
⚡ **Real-time display** - See your countdown updated every second

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Clone the repository
git clone https://github.com/Alberto-Codes/pomodoro-timer.git
cd pomodoro-timer

# Install dependencies
uv sync

# Run the timer
uv run pomodoro-timer start work
```

## Usage

### Start a Work Session (25 minutes)

```bash
uv run pomodoro-timer start work
```

Output:
```
RUNNING: Work - 24:59
RUNNING: Work - 24:58
...
✓ Work session complete! Time for a break.
```

### Start a Break (5 minutes)

```bash
uv run pomodoro-timer start break
```

### Pause the Current Timer

```bash
uv run pomodoro-timer pause
```

### Resume a Paused Timer

```bash
uv run pomodoro-timer resume
```

### Cancel the Current Session

```bash
uv run pomodoro-timer cancel
```

### Check Timer Status

```bash
uv run pomodoro-timer status
```

Output when idle:
```
State: IDLE
No active session
```

Output when running:
```
State: RUNNING
Session Type: Work
Remaining Time: 23:45
```

## The Pomodoro Technique

1. Choose a task to work on
2. Start a 25-minute work session
3. Work without interruption until the timer completes
4. Take a 5-minute break
5. Repeat steps 2-4

This implementation focuses on the core work-break cycle. For more information about the Pomodoro Technique, visit [pomodorotechnique.com](https://francescocirillo.com/products/the-pomodoro-technique).

## Development

### Prerequisites

- Python 3.12+
- uv package manager

### Project Structure

```
src/pomodoro_timer/          # Main application code
├── models/                  # Data models and state management
│   ├── types.py            # SessionType and SessionState enums
│   ├── session.py          # TimerSession class with state machine
│   └── exceptions.py       # Custom exceptions
├── timer/                   # Timer engine and notifications
│   ├── engine.py           # Async countdown loop
│   └── notifications.py    # Completion notifications
└── cli/                     # CLI interface
    ├── commands.py         # Command handlers
    └── display.py          # Terminal display formatting

tests/                       # Test suite
├── unit/                   # Unit tests
└── integration/            # Integration tests
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run in parallel
uv run pytest -n auto
```

### Code Quality

```bash
# Type checking
uv run ty check

# Linting
uv run ruff check src/ tests/

# Auto-fix linting issues
uv run ruff check --fix src/ tests/

# Formatting
uv run ruff format src/ tests/

# Check docstrings
uv run ruff check --select D src/
```

## Technical Details

- **Language**: Python 3.12+
- **Dependencies**: None (stdlib only for runtime)
- **Dev Dependencies**: pytest, pytest-asyncio, pytest-cov, pytest-xdist, freezegun, ruff, ty
- **Architecture**: Event-driven with asyncio
- **State Management**: Finite state machine (IDLE → RUNNING → PAUSED/COMPLETED)
- **Display**: ANSI escape codes for in-place terminal updates
- **Refresh Rate**: 10Hz (0.1s intervals) for smooth display

## Design Principles

✅ **Test-First Development** - 50 tests written before implementation  
✅ **Type Safety** - Full type hints with ty checking  
✅ **Quality Gates** - 97% code coverage, all lints passing  
✅ **Stdlib Only** - Zero runtime dependencies  
✅ **Clean Architecture** - Separation of concerns (models, engine, CLI)

## Limitations

- Sessions are **not persisted** - closing the app resets the timer
- **One session at a time** - cannot run multiple concurrent timers
- **No session history** - no tracking of completed sessions
- **Manual transitions only** - must explicitly start each work/break

These are intentional design decisions to keep the MVP simple and focused.

## License

This project is licensed under the MIT License.

## Acknowledgments

The Pomodoro Technique® and Pomodoro™ are registered trademarks of Francesco Cirillo.
