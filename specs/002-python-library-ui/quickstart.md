# Quickstart Guide: Python Library-Based UI

**Feature**: Python Library-Based UI (002-python-library-ui)  
**Date**: October 17, 2025  
**Audience**: Developers implementing this feature

## Prerequisites

- Python 3.12+ installed
- `uv` package manager installed
- Pomodoro Timer project cloned and working CLI functional
- Familiarity with async/await in Python
- Basic understanding of reactive UI patterns

## Installation

### 1. Install Dependencies

```powershell
# Add NiceGUI for UI framework
uv add nicegui

# Add tomli-w for TOML writing (read is stdlib)
uv add tomli-w

# Sync all dependencies
uv sync
```

### 2. Verify Installation

```powershell
# Check NiceGUI installed
uv run python -c "import nicegui; print(f'NiceGUI {nicegui.__version__}')"

# Expected output: NiceGUI 2.x.x

# Check tomli-w installed
uv run python -c "import tomli_w; print('tomli-w OK')"

# Expected output: tomli-w OK
```

## Project Structure

Create the following directory structure:

```
src/pomodoro_timer/ui/
├── __init__.py              # Public API exports
├── app.py                   # Main NiceGUI application entry point
├── state.py                 # AppState bridge class
├── models.py                # CompletedSession, TimerConfig models
├── database.py              # SQLite database manager
├── config.py                # TOML configuration manager
├── keyboard.py              # Keyboard shortcuts setup
├── components/
│   ├── __init__.py
│   ├── timer_display.py     # Timer countdown display
│   ├── controls.py          # Start/pause/resume/stop buttons
│   ├── history.py           # Session history table
│   └── settings.py          # Settings configuration form
└── pages/
    ├── __init__.py
    └── main.py              # Main page layout
```

## Step-by-Step Implementation

### Step 1: Create Models (`ui/models.py`)

```python
"""Data models for UI layer."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from pomodoro_timer.models.types import SessionType


@dataclass
class CompletedSession:
    """Represents a completed Pomodoro session."""
    
    id: int | None
    session_type: SessionType
    start_time: datetime
    end_time: datetime
    duration_seconds: int
    
    @property
    def duration_display(self) -> str:
        """Format duration for display."""
        minutes = self.duration_seconds // 60
        return f"{minutes} min"
    
    @property
    def date(self) -> datetime.date:
        """Extract date for grouping."""
        return self.start_time.date()
    
    @property
    def time_range_display(self) -> str:
        """Format time range for display."""
        start = self.start_time.strftime("%H:%M")
        end = self.end_time.strftime("%H:%M")
        return f"{start} - {end}"


@dataclass
class TimerConfig:
    """User-configurable timer settings."""
    
    work_duration_minutes: int = 25
    short_break_minutes: int = 5
    long_break_minutes: int = 15
    theme: str = "auto"
    
    MIN_DURATION = 1
    MAX_DURATION = 999
    
    def validate(self) -> None:
        """Validate configuration values.
        
        Raises:
            ValueError: If any value is invalid
        """
        if not (self.MIN_DURATION <= self.work_duration_minutes <= self.MAX_DURATION):
            raise ValueError(f"Work duration must be between {self.MIN_DURATION} and {self.MAX_DURATION}")
        if not (self.MIN_DURATION <= self.short_break_minutes <= self.MAX_DURATION):
            raise ValueError(f"Break duration must be between {self.MIN_DURATION} and {self.MAX_DURATION}")
        if self.theme not in ("auto", "light", "dark"):
            raise ValueError("Theme must be 'auto', 'light', or 'dark'")
    
    @classmethod
    def default(cls) -> "TimerConfig":
        """Create config with default values."""
        return cls()
```

### Step 2: Create State Bridge (`ui/state.py`)

```python
"""Application state bridge between UI and timer engine."""

from nicegui import observables

from pomodoro_timer.models.session import TimerSession
from pomodoro_timer.models.types import SessionState, SessionType
from pomodoro_timer.timer.engine import TimerEngine
from pomodoro_timer.ui.models import CompletedSession, TimerConfig


class AppState:
    """Central application state."""
    
    def __init__(self):
        """Initialize application state."""
        self.session = TimerSession()
        self.engine = TimerEngine(self.session)
        self.history: observables.ObservableList[CompletedSession] = observables.ObservableList()
        self.config = TimerConfig.default()
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage (0-100)."""
        if not self.session.session_type:
            return 0.0
        total = self.session.session_type.duration_seconds
        remaining = self.session.remaining_seconds
        return ((total - remaining) / total) * 100
    
    @property
    def is_idle(self) -> bool:
        """Check if no session active."""
        return self.session.state == SessionState.IDLE
    
    @property
    def is_running(self) -> bool:
        """Check if session running."""
        return self.session.state == SessionState.RUNNING
    
    @property
    def is_paused(self) -> bool:
        """Check if session paused."""
        return self.session.state == SessionState.PAUSED
    
    @property
    def current_time_display(self) -> str:
        """Get formatted time for display."""
        return self.session.formatted_time
    
    @property
    def current_type_display(self) -> str:
        """Get session type for display."""
        if self.session.session_type:
            return self.session.session_type.display_name
        return "Idle"
    
    async def start_work(self) -> None:
        """Start work session."""
        await self.engine.start_work()
    
    async def start_break(self) -> None:
        """Start break session."""
        await self.engine.start_break()
    
    def pause(self) -> None:
        """Pause current session."""
        self.engine.pause()
    
    async def resume(self) -> None:
        """Resume paused session."""
        await self.engine.resume()
    
    def cancel(self) -> None:
        """Cancel current session."""
        self.engine.cancel()


# Global app state instance
app_state = AppState()
```

### Step 3: Create Timer Display Component (`ui/components/timer_display.py`)

```python
"""Timer display component."""

from nicegui import ui

from pomodoro_timer.ui.state import AppState


@ui.refreshable
def timer_display(state: AppState) -> None:
    """Display current timer state.
    
    Args:
        state: Application state to observe
    """
    with ui.card().classes('w-96 text-center'):
        # Time display (large text)
        ui.label(state.current_time_display).classes('text-6xl font-mono')
        
        # Session type
        ui.label(state.current_type_display).classes('text-xl text-gray-600')
        
        # Progress bar
        ui.linear_progress(
            value=state.progress_percentage / 100,
            show_value=False
        ).classes('mt-4')
        
        # State indicator
        if state.is_running:
            ui.badge("Running", color="green")
        elif state.is_paused:
            ui.badge("Paused", color="orange")
        else:
            ui.badge("Idle", color="gray")
```

### Step 4: Create Controls Component (`ui/components/controls.py`)

```python
"""Timer control buttons component."""

import asyncio

from nicegui import ui

from pomodoro_timer.models.exceptions import InvalidStateTransition, SessionAlreadyActive
from pomodoro_timer.ui.state import AppState


def control_buttons(state: AppState) -> None:
    """Display timer control buttons.
    
    Args:
        state: Application state to control
    """
    with ui.row().classes('gap-2 justify-center'):
        # Start Work button (show when idle)
        if state.is_idle:
            ui.button(
                'Start Work',
                on_click=lambda: asyncio.create_task(handle_start_work(state)),
                icon='work'
            ).props('color=primary')
            
            ui.button(
                'Start Break',
                on_click=lambda: asyncio.create_task(handle_start_break(state)),
                icon='coffee'
            ).props('color=secondary')
        
        # Pause button (show when running)
        elif state.is_running:
            ui.button(
                'Pause',
                on_click=lambda: handle_pause(state),
                icon='pause'
            ).props('color=warning')
            
            ui.button(
                'Cancel',
                on_click=lambda: handle_cancel(state),
                icon='stop'
            ).props('color=negative')
        
        # Resume button (show when paused)
        elif state.is_paused:
            ui.button(
                'Resume',
                on_click=lambda: asyncio.create_task(handle_resume(state)),
                icon='play_arrow'
            ).props('color=positive')
            
            ui.button(
                'Cancel',
                on_click=lambda: handle_cancel(state),
                icon='stop'
            ).props('color=negative')


async def handle_start_work(state: AppState) -> None:
    """Handle start work button click."""
    try:
        await state.start_work()
    except SessionAlreadyActive as e:
        ui.notify(str(e), type='negative')


async def handle_start_break(state: AppState) -> None:
    """Handle start break button click."""
    try:
        await state.start_break()
    except SessionAlreadyActive as e:
        ui.notify(str(e), type='negative')


def handle_pause(state: AppState) -> None:
    """Handle pause button click."""
    try:
        state.pause()
    except InvalidStateTransition as e:
        ui.notify(str(e), type='negative')


async def handle_resume(state: AppState) -> None:
    """Handle resume button click."""
    try:
        await state.resume()
    except InvalidStateTransition as e:
        ui.notify(str(e), type='negative')


def handle_cancel(state: AppState) -> None:
    """Handle cancel button click."""
    state.cancel()
```

### Step 5: Create Main Page (`ui/pages/main.py`)

```python
"""Main application page."""

from nicegui import ui

from pomodoro_timer.ui.components.controls import control_buttons
from pomodoro_timer.ui.components.timer_display import timer_display
from pomodoro_timer.ui.state import app_state


@ui.refreshable
def main_content() -> None:
    """Main page content that refreshes."""
    with ui.column().classes('items-center gap-8 p-8'):
        # Timer display
        timer_display(app_state)
        
        # Control buttons
        control_buttons(app_state)


def main_page() -> None:
    """Main application page."""
    # Page title
    ui.page_title('Pomodoro Timer')
    
    # Header
    with ui.header().classes('items-center justify-between'):
        ui.label('Pomodoro Timer').classes('text-2xl')
    
    # Main content
    main_content()
    
    # Setup automatic refresh every 1 second
    ui.timer(1.0, lambda: main_content.refresh())
```

### Step 6: Create Application Entry Point (`ui/app.py`)

```python
"""NiceGUI application entry point."""

from nicegui import ui

from pomodoro_timer.ui.pages.main import main_page
from pomodoro_timer.ui.state import app_state


def run_ui() -> None:
    """Run the NiceGUI user interface."""
    # Define main page route
    @ui.page('/')
    def index():
        main_page()
    
    # Run the app
    ui.run(
        title='Pomodoro Timer',
        port=8080,
        show=True,  # Automatically open browser
        reload=False,  # Disable auto-reload in production
    )


if __name__ == '__main__':
    run_ui()
```

### Step 7: Update Main Entry Point (`__init__.py`)

```python
"""Pomodoro Timer - CLI and UI application."""

import sys


def main() -> None:
    """Main entry point for Pomodoro Timer."""
    # Check for --ui flag
    if '--ui' in sys.argv:
        from pomodoro_timer.ui.app import run_ui
        run_ui()
    else:
        # Existing CLI code
        print("CLI mode (not yet implemented)")
        print("Use --ui flag to launch visual interface")


if __name__ == '__main__':
    main()
```

## Running the Application

### Launch UI Mode

```powershell
# Run via entry point
uv run pomodoro-timer --ui

# Or run directly
uv run python -m pomodoro_timer --ui

# Browser should automatically open to http://localhost:8080
```

### Expected Behavior

1. Browser opens to `http://localhost:8080`
2. See "Pomodoro Timer" header
3. See timer display showing "00:00" and "Idle"
4. See "Start Work" and "Start Break" buttons
5. Click "Start Work":
   - Timer changes to "25:00"
   - State changes to "Running"
   - Progress bar starts filling
   - Buttons change to "Pause" and "Cancel"
6. Timer counts down every second
7. Click "Pause":
   - Timer stops counting
   - State changes to "Paused"
   - Buttons change to "Resume" and "Cancel"

## Testing Your Implementation

### Manual Testing Checklist

- [ ] App launches and browser opens
- [ ] Timer displays "00:00" when idle
- [ ] "Start Work" button starts 25-minute timer
- [ ] Timer counts down every second
- [ ] "Pause" button pauses timer
- [ ] "Resume" button resumes from paused time
- [ ] "Cancel" button returns to idle
- [ ] Progress bar fills as timer progresses
- [ ] State badges update correctly (Running/Paused/Idle)

### Automated Testing

```powershell
# Run unit tests
uv run pytest tests/unit/ui/ -v

# Run integration tests (requires NiceGUI)
uv run pytest tests/integration/ui/ -v -p nicegui.testing.plugin

# Run all tests with coverage
uv run pytest --cov=src/pomodoro_timer/ui --cov-report=term-missing
```

### Example Test (Using `user` Fixture)

Create `tests/integration/ui/test_basic_timer.py`:

```python
"""Basic timer UI tests."""

import asyncio

from nicegui.testing import User

from pomodoro_timer.ui.state import app_state


async def test_start_work_session(user: User) -> None:
    """Test starting a work session."""
    await user.open('/')
    
    # Should see idle state
    await user.should_see('00:00')
    await user.should_see('Idle')
    
    # Click Start Work
    user.find('Start Work').click()
    
    # Should see work session started
    await user.should_see('25:00')
    await user.should_see('Work')
    await user.should_see('Running')
    
    # Wait for timer to tick
    await asyncio.sleep(1.1)
    
    # Should see time decreased
    await user.should_see('24:59')
```

## Next Steps

After completing basic timer display and controls (P1), proceed to:

1. **P2: Session History** (create `history.py` component, `database.py` manager)
2. **P3: Settings** (create `settings.py` component, `config.py` manager)
3. **Keyboard Shortcuts** (create `keyboard.py` setup)
4. **Polish** (styling, animations, notifications on completion)

## Common Issues

### Issue: Browser doesn't open

**Solution**: Check if port 8080 is already in use. Try different port:

```python
ui.run(port=8081, show=True)
```

### Issue: Timer doesn't update

**Solution**: Verify `ui.timer` is set up in main page:

```python
ui.timer(1.0, lambda: main_content.refresh())
```

### Issue: Buttons don't respond

**Solution**: Check async event handlers use `asyncio.create_task()`:

```python
on_click=lambda: asyncio.create_task(state.start_work())
```

### Issue: Type checking fails

**Solution**: Ensure all imports have type hints:

```python
from nicegui import ui
from pomodoro_timer.ui.state import AppState  # Not just: from .state import ...
```

## Resources

- **NiceGUI Documentation**: https://nicegui.io/documentation
- **NiceGUI Examples**: https://github.com/zauberzeug/nicegui/tree/main/examples
- **Project Spec**: `specs/002-python-library-ui/spec.md`
- **Data Model**: `specs/002-python-library-ui/data-model.md`
- **Contracts**: `specs/002-python-library-ui/contracts/ui-components.md`
- **Research**: `specs/002-python-library-ui/research.md`

## Getting Help

1. Check NiceGUI documentation for component usage
2. Review existing tests in `tests/integration/test_timer_workflows.py`
3. Examine existing timer engine code in `src/pomodoro_timer/timer/engine.py`
4. Ask questions in project discussions or create GitHub issue

## Summary

You now have:
- ✅ Basic UI structure with NiceGUI
- ✅ State bridge connecting UI to timer engine
- ✅ Timer display component showing countdown
- ✅ Control buttons for start/pause/resume/cancel
- ✅ Real-time updates via `ui.timer`
- ✅ Reactive UI via `@ui.refreshable` decorator
- ✅ Clean separation between UI and business logic

Next: Implement P2 (Session History) and P3 (Settings) features!
