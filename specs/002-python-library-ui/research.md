# Research: Python Library-Based UI with NiceGUI

**Feature**: Python Library-Based UI (002-python-library-ui)  
**Date**: October 17, 2025  
**Researcher**: GitHub Copilot  
**Status**: Complete

## Executive Summary

**Decision**: Use NiceGUI as the Python web UI framework for the Pomodoro Timer visual interface.

**Rationale**: NiceGUI is a modern, reactive Python web framework that perfectly matches the project's requirements for a lightweight, Pythonic UI library. It provides built-in real-time updates (critical for countdown timers), native async/await support (integrates seamlessly with existing TimerEngine), and excellent testing capabilities that align with the project's test-first principles.

**Key Findings**:
- NiceGUI has native `ui.timer` for periodic UI updates (perfect for countdown display)
- Full async/await support - integrates directly with existing `TimerEngine`
- Reactive state management via binding and `@ui.refreshable` decorator
- Excellent testing story: `user` fixture for fast Python-level tests, `screen` fixture for browser tests
- Uses FastAPI backend - lightweight, runs on localhost by default
- No separate frontend build step required - pure Python development

## Technology Evaluation: NiceGUI

### What is NiceGUI?

**Official Documentation**: https://nicegui.io/documentation

NiceGUI is an open-source Python library for creating graphical user interfaces that run in the browser. It follows a "backend-first philosophy" where all web development details are handled automatically, allowing developers to focus on writing Python code.

**Key Characteristics**:
- **Declarative UI**: Uses Python's `with` statement for nested component structure (similar to Flutter/SwiftUI)
- **Reactive Framework**: Automatic UI updates when bound data changes
- **Async-First**: Built on FastAPI with full async/await support
- **Browser-Based**: Runs as local web server, UI accessed via browser (can also run in native window mode)
- **Component Library**: Rich set of pre-built components (buttons, labels, cards, tables, charts, etc.)
- **Based on Quasar/Vue**: Uses Quasar component framework under the hood, styled with Tailwind CSS

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           Vue.js + Quasar Components                   │  │
│  │  (Auto-generated, dev doesn't write frontend code)     │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────────────────┘
                   │ WebSocket (automatic updates)
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                   FastAPI Server                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              NiceGUI Python Code                       │  │
│  │  - UI Components (ui.button, ui.label, etc.)          │  │
│  │  - Event Handlers (on_click, timers, etc.)            │  │
│  │  - State Management (binding, refreshable)            │  │
│  │  - Integration with existing Python code              │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           Existing Pomodoro Timer                      │  │
│  │  - TimerEngine (async countdown loop)                 │  │
│  │  - TimerSession (state management)                    │  │
│  │  - SessionType (WORK/BREAK enums)                     │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Real-Time Updates: `ui.timer`

**Documentation**: https://nicegui.io/documentation/timer

NiceGUI provides `ui.timer(interval, callback)` for periodic UI updates - perfect for countdown timers:

```python
from nicegui import ui

# Update every 1 second
ui.timer(1.0, lambda: label.set_text(session.formatted_time))
```

**Features**:
- Accepts async callbacks (can call `await session.tick()`)
- Can be paused/resumed via `.active` property
- Can be cancelled via `.cancel()` method
- Configurable `interval` (can change dynamically)
- Supports `once=True` for delayed execution (useful for notifications)

**Integration Strategy**: Use `ui.timer` to bridge existing `TimerEngine` with UI display:
- Timer calls `session.tick()` periodically (existing behavior)
- UI elements bound to session properties update automatically
- No duplication of countdown logic - UI observes existing state

### Async Integration

NiceGUI is fully async/await compatible - the existing `TimerEngine` uses `asyncio`, which integrates perfectly:

```python
async def start_work_session():
    """Start work session - integrates existing async engine"""
    await timer_engine.start_work()
    # UI updates automatically via bound state
```

**Async Patterns**:
- Event handlers can be `async def` functions
- Timer callbacks can be coroutines
- Can use `await asyncio.sleep()` in UI code
- Background tasks via `background_tasks.create()`
- CPU-bound work via `run.cpu_bound()`, IO-bound via `run.io_bound()`

### State Management

**Option 1: Property Binding** (Recommended for simple cases)

```python
from nicegui import ui

# Two-way binding
label = ui.label().bind_text_from(session, 'formatted_time')

# Bind visibility
button.bind_visibility_from(session, 'is_active', backward=lambda v: not v)
```

**Option 2: Refreshable UI** (Recommended for complex updates)

```python
from nicegui import ui

@ui.refreshable
def timer_display():
    ui.label(f"Time: {session.formatted_time}")
    ui.label(f"State: {session.state.display_name}")

# Refresh from timer callback
ui.timer(1.0, lambda: timer_display.refresh())
```

**Option 3: Observable Collections** (For lists/dicts)

```python
from nicegui import observables

# For session history (P2 feature)
sessions = observables.ObservableList()
ui.table(columns=[...]).bind_rows_from(sessions)
```

**Recommendation**: Use **Property Binding** for timer display (simplest, most reactive), **Refreshable UI** for complex views, **Observable Collections** for session history table.

### Testing Strategy

**Documentation**: https://nicegui.io/documentation/section_testing

NiceGUI provides excellent testing capabilities that align with the project's test-first principles:

**Option 1: User Fixture (Recommended - Fast)**

Simulates user interaction at Python level - no browser needed:

```python
from nicegui.testing import User

async def test_start_timer(user: User) -> None:
    await user.open('/')
    await user.should_see('00:00')
    user.find('Start Work').click()
    await user.should_see('25:00')
    await asyncio.sleep(1.1)  # Wait for timer tick
    await user.should_see('24:59')
```

**Advantages**:
- Fast execution (no browser overhead)
- Easy to write (readable, story-like API)
- Perfect for acceptance criteria testing
- Aligns with test pyramid best practices

**Option 2: Screen Fixture (Only if Needed - Slow)**

Runs real headless browser via Selenium:

```python
from nicegui.testing import Screen

def test_visual_timer(screen: Screen) -> None:
    screen.open('/')
    screen.should_contain('00:00')
    screen.click('Start Work')
    screen.should_contain('25:00')
```

**When to Use**: Browser-specific behavior, visual regression testing, complex JavaScript interactions.

**Configuration** (`pytest.ini`):

```ini
[pytest]
asyncio_mode = auto
main_file = main.py
addopts = -p nicegui.testing.plugin
```

**Strategy**: Use `user` fixture for all acceptance criteria tests (P1, P2, P3), reserve `screen` fixture for edge cases if needed.

### UI Component Organization

**Recommended Structure**:

```
src/pomodoro_timer/ui/
├── __init__.py           # Public API
├── app.py                # Main NiceGUI application (ui.run entry point)
├── state.py              # Bridge between UI and TimerEngine
├── components/
│   ├── __init__.py
│   ├── timer_display.py  # P1: Timer countdown display component
│   ├── controls.py       # P1: Start/pause/resume/stop buttons
│   ├── history.py        # P2: Session history table
│   └── settings.py       # P3: Duration configuration
└── pages/
    ├── __init__.py
    └── main.py           # Main page layout
```

**Component Pattern**:

```python
# components/timer_display.py
from nicegui import ui
from pomodoro_timer.ui.state import app_state

@ui.refreshable
def timer_display():
    """Display current timer state"""
    with ui.card().classes('w-96'):
        session = app_state.session
        ui.label(session.formatted_time).classes('text-6xl text-center')
        ui.label(session.session_type.display_name if session.session_type else 'Idle')
        ui.linear_progress(value=app_state.progress_percentage / 100)
```

**Page Pattern**:

```python
# pages/main.py
from nicegui import ui
from pomodoro_timer.ui.components import timer_display, controls, history

def main_page():
    """Main application page"""
    with ui.column().classes('items-center gap-4 p-4'):
        timer_display()
        controls()
        ui.separator()
        history()
```

## Storage Solution for Session History (P2)

### Requirement

- **FR-007**: System MUST show a history view listing completed sessions with timestamps
- **SC-005**: Session history accurately displays 100% of completed sessions
- **SC-008**: User settings persist across application restarts

### Options Evaluated

**Option 1: SQLite** (Recommended)

**Pros**:
- Built into Python stdlib (no extra dependency)
- ACID transactions (reliable persistence)
- Easy to query (SQL for filtering/sorting by date)
- Supports proper data types (datetime, integers)
- Scales well (thousands of sessions without performance issues)

**Cons**:
- Slightly more complex setup than JSON
- Requires schema definition

**Implementation**:

```python
import sqlite3
from pathlib import Path

DB_PATH = Path.home() / '.config' / 'pomodoro-timer' / 'sessions.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_type TEXT NOT NULL,
            start_time REAL NOT NULL,
            end_time REAL NOT NULL,
            duration_seconds INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
```

**Option 2: JSON File**

**Pros**:
- Simplest implementation
- Human-readable format
- Easy debugging

**Cons**:
- No transactions (risk of corruption on crash)
- Inefficient for large datasets (load entire file)
- Manual serialization of datetimes
- No built-in querying (must filter in Python)

**Option 3: In-Memory Only**

**Pros**:
- Fastest access
- Simplest code

**Cons**:
- Loses all history on app restart (violates FR-011, SC-008)
- Not suitable for production use

### Decision: SQLite

**Rationale**: SQLite provides the best balance of simplicity (stdlib, no dependencies), reliability (ACID transactions), and functionality (queryable, supports date filtering for P2 requirement of grouping by date). Performance is excellent for expected dataset size (<10,000 sessions). Aligns with project's simplicity principle while meeting all functional requirements.

**Schema**:

```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_type TEXT NOT NULL CHECK(session_type IN ('WORK', 'BREAK')),
    start_time REAL NOT NULL,  -- Unix timestamp
    end_time REAL NOT NULL,    -- Unix timestamp
    duration_seconds INTEGER NOT NULL,
    created_at REAL DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX idx_session_type ON sessions(session_type);
CREATE INDEX idx_created_at ON sessions(created_at DESC);
```

## Settings Persistence (P3)

### Requirement

- **FR-008-010**: Configure work/short break/long break durations
- **FR-011**: Settings persist between application restarts
- **SC-008**: Settings persist with 100% reliability

### Options Evaluated

**Option 1: TOML Configuration File** (Recommended)

**Pros**:
- Modern, human-readable format (aligns with pyproject.toml usage)
- Comments supported (can document default values)
- Python stdlib support via `tomllib` (read) and `tomli-w` (write - external dependency)
- Strong typing (integers, strings, booleans)
- Natural fit for application configuration

**Cons**:
- Requires `tomli-w` dependency for writing (read-only in stdlib)

**Implementation**:

```python
import tomllib
from pathlib import Path

CONFIG_PATH = Path.home() / '.config' / 'pomodoro-timer' / 'config.toml'

# Default config
DEFAULT_CONFIG = """
[timer]
work_duration_minutes = 25
short_break_minutes = 5
long_break_minutes = 15

[ui]
theme = "auto"  # auto, light, dark
"""

def load_config():
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(DEFAULT_CONFIG)
    
    with open(CONFIG_PATH, 'rb') as f:
        return tomllib.load(f)
```

**Option 2: JSON Configuration File**

**Pros**:
- Stdlib support for read/write (no dependencies)
- Simple, widely understood format

**Cons**:
- No comments support (less user-friendly)
- Less readable than TOML for config files

**Option 3: NiceGUI `app.storage.user`**

**Documentation**: https://nicegui.io/documentation/storage

NiceGUI provides persistent storage via `app.storage.user`:

```python
from nicegui import app

# Persists to file on server, unique per browser
app.storage.user['work_duration'] = 25
```

**Pros**:
- Built into NiceGUI (no extra code)
- Automatic persistence
- Per-user support (if needed)

**Cons**:
- File format is pickle (not human-editable)
- Tied to NiceGUI (can't be used by CLI)
- Less portable

### Decision: TOML Configuration File

**Rationale**: TOML aligns with project's modern Python practices (pyproject.toml), supports comments for user guidance, and is easily human-editable. The single dependency (`tomli-w`) is justified by superior user experience. Configuration is shared between CLI and UI modes, so it should not be NiceGUI-specific. File location (`~/.config/pomodoro-timer/config.toml`) follows XDG Base Directory specification.

**Storage Location**:
- **Linux/macOS**: `~/.config/pomodoro-timer/`
- **Windows**: `%USERPROFILE%\.config\pomodoro-timer\`

## Integration Architecture

### Separation of Concerns

The UI should be a **presentation layer** that observes and controls the existing timer engine without duplicating logic:

```
┌─────────────────────────────────────────────────────────────┐
│                       UI Layer (New)                         │
│  - NiceGUI components (display, controls, history, settings) │
│  - User interaction handlers                                 │
│  - State observation via binding/refreshable                 │
│  - No business logic                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Commands / Events
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  State Bridge (New)                          │
│  - Connects UI to TimerEngine                                │
│  - Exposes bindable properties                               │
│  - Translates UI events to engine commands                   │
│  - Progress calculation (percentage)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ start_work(), pause(), etc.
                         │
┌────────────────────────▼────────────────────────────────────┐
│               Timer Engine (Existing)                        │
│  - TimerEngine (async countdown)                             │
│  - TimerSession (state management)                           │
│  - SessionType (durations)                                   │
│  - ALL business logic lives here                             │
└─────────────────────────────────────────────────────────────┘
```

### State Bridge Pattern

Create a lightweight bridge class that exposes timer state to the UI:

```python
# ui/state.py
from nicegui import observables
from pomodoro_timer.timer.engine import TimerEngine
from pomodoro_timer.models.session import TimerSession

class AppState:
    """Bridge between UI and timer engine"""
    
    def __init__(self):
        self.session = TimerSession()
        self.engine = TimerEngine(self.session)
        self.history = observables.ObservableList()
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage for progress bar"""
        if not self.session.session_type:
            return 0.0
        total = self.session.session_type.duration_seconds
        remaining = self.session.remaining_seconds
        return ((total - remaining) / total) * 100
    
    async def start_work(self):
        """Start work session"""
        await self.engine.start_work()
    
    async def pause(self):
        """Pause current session"""
        self.engine.pause()
    
    # ... other control methods

# Global app state (single instance)
app_state = AppState()
```

**Benefits**:
- UI components never directly access TimerEngine (loose coupling)
- Easy to mock `AppState` for UI tests
- Progress calculation centralized (not duplicated across components)
- Observable history list auto-updates UI table

## Keyboard Shortcuts (FR-015)

**Documentation**: https://nicegui.io/documentation/keyboard

NiceGUI provides `ui.keyboard()` for global keyboard event handling:

```python
from nicegui import ui

def setup_keyboard_shortcuts():
    ui.keyboard(
        on_key=lambda e: handle_key(e.key),
        active=True
    )

def handle_key(key: str):
    if key == ' ':  # Spacebar
        # Start or pause
        if app_state.session.state == SessionState.IDLE:
            asyncio.create_task(app_state.start_work())
        elif app_state.session.state == SessionState.RUNNING:
            app_state.pause()
        elif app_state.session.state == SessionState.PAUSED:
            asyncio.create_task(app_state.resume())
    elif key == 'Escape':
        app_state.cancel()
```

**Shortcuts Specification**:
- `Space`: Start (if idle) / Pause (if running) / Resume (if paused)
- `Escape`: Stop/Cancel
- `W`: Start work session
- `B`: Start break session

## Alternatives Considered

### Tkinter (Rejected)

**Pros**: Stdlib (no dependencies), native desktop windows, mature

**Cons**:
- Outdated look/feel (not modern)
- Poor async support (requires custom event loop integration)
- Limited component library
- No web deployment option
- Difficult to test automatically

**Verdict**: Rejected - does not meet "most modern python web ui" requirement from spec.

### Streamlit (Rejected)

**Pros**: Very simple API, popular for dashboards, good for data viz

**Cons**:
- Rerun model (entire script re-executes on interaction) - incompatible with persistent timer state
- Poor for real-time updates (no built-in timer mechanism)
- Limited control over UI layout/styling
- Not designed for stateful applications like timers

**Verdict**: Rejected - execution model fundamentally incompatible with continuous countdown timer.

### Flask + React (Rejected)

**Pros**: Industry standard, maximum flexibility, large ecosystem

**Cons**:
- Requires JavaScript development (separate frontend codebase)
- Build step complexity (webpack, npm, etc.)
- Violates "simple python library" requirement
- Much higher complexity for simple timer UI

**Verdict**: Rejected - too complex, requires non-Python skills, violates simplicity principle.

### Textual (Rejected)

**Pros**: Modern TUI framework, pure Python, excellent for CLI apps

**Cons**:
- Terminal-based (not web-based)
- Does not meet "web ui" requirement
- Limited to terminal capabilities (no rich graphics)

**Verdict**: Rejected - not a web UI framework.

## Implementation Checklist

- [ ] Add `nicegui` dependency via `uv add nicegui`
- [ ] Add `tomli-w` dependency via `uv add tomli-w` (for settings write)
- [ ] Create `src/pomodoro_timer/ui/` module structure
- [ ] Implement `state.py` bridge between UI and TimerEngine
- [ ] Implement P1 components (timer display, controls)
- [ ] Implement P2 components (session history with SQLite)
- [ ] Implement P3 components (settings form with TOML config)
- [ ] Add keyboard shortcuts
- [ ] Write acceptance tests using `user` fixture
- [ ] Update main entry point to support `--ui` flag
- [ ] Document UI mode in README.md

## References

- **NiceGUI Documentation**: https://nicegui.io/documentation
- **NiceGUI Timer**: https://nicegui.io/documentation/timer
- **NiceGUI Testing**: https://nicegui.io/documentation/section_testing
- **NiceGUI Refreshable**: https://nicegui.io/documentation/refreshable
- **NiceGUI GitHub**: https://github.com/zauberzeug/nicegui
- **SQLite Python Documentation**: https://docs.python.org/3/library/sqlite3.html
- **TOML Specification**: https://toml.io/en/
- **Python tomllib**: https://docs.python.org/3/library/tomllib.html
