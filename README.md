# Pomodoro Timer

A modern Pomodoro timer built with Python 3.12+ that helps you stay focused using the Pomodoro Technique®. Available in both **CLI** and **Web UI** modes!

## Features

### Core Features
🎯 **25-minute work sessions** - Standard Pomodoro work intervals  
☕ **5-minute breaks** - Short breaks between work sessions  
⏸️ **Pause & Resume** - Flexible control over your timer  
❌ **Cancel anytime** - Reset and start fresh when needed  
🔔 **Visual & Audio notifications** - Get notified when sessions complete  
⚡ **Real-time display** - See your countdown updated every second

### Web UI Mode (New!)
🌐 **Visual Timer** - Beautiful countdown display in your browser  
📊 **Session History** - Track all completed sessions with timestamps  
⚙️ **Customizable Durations** - Configure work/break times (1-999 minutes)  
⌨️ **Keyboard Shortcuts** - Space (start/pause), Escape (cancel), W (work), B (break)  
💾 **Persistent Settings** - Config saved to TOML, history to SQLite

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

### Web UI Mode (Recommended)

Launch the visual timer in your web browser:

```bash
uv run pomodoro-timer --ui
```

The UI opens at `http://localhost:8080` with:
- **Visual countdown timer** with MM:SS display
- **Progress bar** showing completion percentage
- **Control buttons**: Start Work, Start Break, Pause, Resume, Cancel
- **Session history** table with all completed sessions
- **Settings dialog** to customize timer durations
- **Keyboard shortcuts** for quick control

**Keyboard Shortcuts**:
- `Space` - Start/Pause/Resume (context-sensitive)
- `Escape` - Cancel current session
- `W` - Start work session (when idle)
- `B` - Start break session (when idle)

### CLI Mode (Terminal)

For command-line usage, use the standard commands:

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
├── ui/                      # Web UI (NiceGUI-based)
│   ├── app.py              # UI application entry point
│   ├── state.py            # UI/Engine state bridge
│   ├── models.py           # UI data models
│   ├── database.py         # SQLite session history
│   ├── config.py           # TOML configuration
│   ├── keyboard.py         # Keyboard shortcuts
│   ├── components/         # Reusable UI components
│   │   ├── timer_display.py
│   │   ├── controls.py
│   │   ├── history.py
│   │   └── settings.py
│   └── pages/              # UI pages
│       └── main.py         # Main page layout
└── cli/                     # CLI interface
    ├── commands.py         # Command handlers
    └── display.py          # Terminal display formatting

tests/                       # Test suite
├── unit/                   # Unit tests
├── integration/            # Integration tests
└── ui/                     # UI acceptance tests
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
- **Core Dependencies**: None (stdlib only for CLI runtime)
- **UI Dependencies**: NiceGUI 3.0.4 (web UI framework), tomli-w 1.2.0 (TOML writing)
- **Dev Dependencies**: pytest, pytest-asyncio, pytest-cov, pytest-xdist, freezegun, ruff, ty
- **Architecture**: Event-driven with asyncio
- **State Management**: Finite state machine (IDLE → RUNNING → PAUSED/COMPLETED)
- **UI Framework**: NiceGUI (FastAPI + Vue 3)
- **Database**: SQLite (session history)
- **Config Format**: TOML (`~/.config/pomodoro-timer/config.toml`)
- **Display**: ANSI escape codes (CLI) / Reactive components (UI)
- **Refresh Rate**: 10Hz (CLI), 1Hz (UI)

## Design Principles

✅ **Test-First Development** - 200+ tests written, 98% passing  
✅ **Type Safety** - Full type hints with ty checking  
✅ **Quality Gates** - 95%+ code coverage, all lints passing  
✅ **Separation of Concerns** - Clean architecture (models, engine, UI, CLI)  
✅ **Progressive Enhancement** - CLI works standalone, UI adds features

## Feature Comparison: CLI vs UI

| Feature | CLI Mode | UI Mode |
|---------|----------|---------|
| Start/Stop Timer | ✅ Commands | ✅ Buttons + Keyboard |
| Visual Countdown | ✅ Terminal | ✅ Browser (MM:SS) |
| Progress Bar | ❌ | ✅ Visual bar + percentage |
| Session History | ❌ | ✅ Persistent SQLite |
| Custom Durations | ❌ | ✅ Settings dialog |
| Keyboard Shortcuts | ❌ | ✅ Space, Esc, W, B |
| Auto-refresh | ✅ 10Hz | ✅ 1Hz |
| Notifications | ✅ Terminal | ✅ Browser + Terminal |

## Limitations

### CLI Mode
- Sessions are **not persisted** - closing the app resets the timer
- **One session at a time** - cannot run multiple concurrent timers
- **No session history** - no tracking of completed sessions
- **No configuration** - durations are fixed (25/5 minutes)

### UI Mode  
- Requires web browser
- Single user (no multi-user support)
- Local storage only (no cloud sync)

These are intentional design decisions to keep the implementation simple and focused.

## License

This project is licensed under the MIT License.

## Acknowledgments

The Pomodoro Technique® and Pomodoro™ are registered trademarks of Francesco Cirillo.
