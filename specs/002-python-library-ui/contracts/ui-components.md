# UI Component Contracts

**Feature**: Python Library-Based UI (002-python-library-ui)  
**Date**: October 17, 2025  
**Type**: Internal API Contracts

## Overview

This document defines the contracts (interfaces) for UI components and their interactions with the state layer. These are **not** REST/GraphQL APIs (this is a local application), but rather Python API contracts between UI components and the application state.

## State Bridge Contract: `AppState`

**Module**: `pomodoro_timer.ui.state`

### Public Interface

```python
from nicegui import observables
from pomodoro_timer.models.session import TimerSession
from pomodoro_timer.models.types import SessionType, SessionState
from pomodoro_timer.timer.engine import TimerEngine
from pomodoro_timer.ui.models import CompletedSession, TimerConfig

class AppState:
    """Central application state bridge between UI and timer engine."""
    
    # ===== Properties (Read-Only) =====
    
    @property
    def session(self) -> TimerSession:
        """Current timer session.
        
        Returns:
            The active TimerSession instance containing current state.
        """
        ...
    
    @property
    def engine(self) -> TimerEngine:
        """Timer engine instance.
        
        Returns:
            The TimerEngine managing the countdown loop.
        """
        ...
    
    @property
    def history(self) -> observables.ObservableList[CompletedSession]:
        """Observable list of completed sessions.
        
        Returns:
            List that automatically notifies UI when sessions are added.
        """
        ...
    
    @property
    def config(self) -> TimerConfig:
        """Current timer configuration.
        
        Returns:
            The current TimerConfig with user settings.
        """
        ...
    
    # ===== Computed Properties (Read-Only) =====
    
    @property
    def progress_percentage(self) -> float:
        """Progress through current session as percentage.
        
        Returns:
            0.0 if idle, 0-100 if active session, based on time elapsed.
            
        Example:
            - Idle: 0.0
            - 5 min into 25 min work: 20.0
            - 24 min into 25 min work: 96.0
        """
        ...
    
    @property
    def is_idle(self) -> bool:
        """Check if no session is active.
        
        Returns:
            True if session.state == SessionState.IDLE
        """
        ...
    
    @property
    def is_running(self) -> bool:
        """Check if session is running.
        
        Returns:
            True if session.state == SessionState.RUNNING
        """
        ...
    
    @property
    def is_paused(self) -> bool:
        """Check if session is paused.
        
        Returns:
            True if session.state == SessionState.PAUSED
        """
        ...
    
    @property
    def current_time_display(self) -> str:
        """Formatted time for display.
        
        Returns:
            "MM:SS" format (e.g., "25:00", "04:37")
            "00:00" if idle.
        """
        ...
    
    @property
    def current_type_display(self) -> str:
        """Session type for display.
        
        Returns:
            "Work", "Break", or "Idle"
        """
        ...
    
    # ===== Control Methods (Async) =====
    
    async def start_work(self) -> None:
        """Start a new work session.
        
        Raises:
            SessionAlreadyActive: If session already running or paused.
            
        Postconditions:
            - session.state == SessionState.RUNNING
            - session.session_type == SessionType.WORK
            - session.remaining_seconds == work_duration * 60
        """
        ...
    
    async def start_break(self) -> None:
        """Start a new break session.
        
        Raises:
            SessionAlreadyActive: If session already running or paused.
            
        Postconditions:
            - session.state == SessionState.RUNNING
            - session.session_type == SessionType.BREAK
            - session.remaining_seconds == break_duration * 60
        """
        ...
    
    def pause(self) -> None:
        """Pause the currently running session.
        
        Raises:
            InvalidStateTransition: If state is not RUNNING.
            
        Postconditions:
            - session.state == SessionState.PAUSED
            - session.remaining_seconds preserved
        """
        ...
    
    async def resume(self) -> None:
        """Resume a paused session.
        
        Raises:
            InvalidStateTransition: If state is not PAUSED.
            
        Postconditions:
            - session.state == SessionState.RUNNING
            - Countdown continues from paused time
        """
        ...
    
    def cancel(self) -> None:
        """Cancel the current session and return to idle.
        
        Postconditions:
            - session.state == SessionState.IDLE
            - session.session_type == None
            - session.remaining_seconds == 0
        """
        ...
    
    # ===== History Methods =====
    
    def record_completion(self) -> None:
        """Save completed session to history and database.
        
        Preconditions:
            - session.state == SessionState.COMPLETED
            
        Postconditions:
            - Completed session added to database
            - Session appended to history observable list
            - UI automatically updates via observable
            
        Raises:
            ValueError: If session is not in COMPLETED state.
        """
        ...
    
    def load_history(self, limit: int = 100) -> list[CompletedSession]:
        """Load recent session history from database.
        
        Args:
            limit: Maximum number of sessions to load (default: 100)
            
        Returns:
            List of CompletedSession objects, most recent first.
            
        Postconditions:
            - history observable list populated
            - UI automatically updates via observable
        """
        ...
    
    def get_history_by_date(self, date: datetime.date) -> list[CompletedSession]:
        """Get sessions for a specific date.
        
        Args:
            date: Date to filter by (year, month, day)
            
        Returns:
            List of sessions that started on the given date,
            ordered by start_time ascending.
        """
        ...
    
    def clear_history(self) -> None:
        """Clear all session history.
        
        Postconditions:
            - Database sessions table emptied
            - history observable list cleared
            - UI automatically updates via observable
            
        Warning:
            This is destructive and cannot be undone.
        """
        ...
    
    # ===== Configuration Methods =====
    
    def load_config(self) -> TimerConfig:
        """Load configuration from TOML file.
        
        Returns:
            TimerConfig with user settings, or defaults if file not found.
            
        Postconditions:
            - self.config updated
            - config applied to SessionType durations
            
        Side Effects:
            - Creates default config file if missing
            - Logs error if file corrupted (uses defaults)
        """
        ...
    
    def save_config(self, config: TimerConfig) -> None:
        """Save configuration to TOML file.
        
        Args:
            config: Configuration to save
            
        Preconditions:
            - config must be valid (durations 1-999, valid theme)
            
        Postconditions:
            - Config written to ~/.config/pomodoro-timer/config.toml
            - self.config updated
            - config applied to SessionType durations
            
        Raises:
            ValueError: If config validation fails
            OSError: If file cannot be written
        """
        ...
    
    def apply_config(self, config: TimerConfig) -> None:
        """Apply configuration to SessionType durations.
        
        Args:
            config: Configuration to apply
            
        Postconditions:
            - SessionType.WORK.duration_seconds = config.work_duration_minutes * 60
            - SessionType.BREAK.duration_seconds = config.short_break_minutes * 60
            
        Note:
            This modifies module-level enum values. New sessions will use
            updated durations. Active sessions are not affected.
        """
        ...
```

### Event Callbacks

UI components can register callbacks for state changes:

```python
# Example: React to session completion
@app_state.session.on_state_change
def handle_state_change(new_state: SessionState):
    if new_state == SessionState.COMPLETED:
        app_state.record_completion()
        ui.notify("Session complete!")
```

**Note**: This is a design pattern suggestion. NiceGUI handles reactivity via property binding and timers, so explicit event callbacks may not be needed.

## Component Contracts

### Timer Display Component

**Module**: `pomodoro_timer.ui.components.timer_display`

```python
@ui.refreshable
def timer_display(state: AppState) -> None:
    """Display current timer state.
    
    Args:
        state: Application state to observe
        
    UI Elements:
        - Large time display (formatted as MM:SS)
        - Session type label (Work/Break/Idle)
        - Progress bar (0-100%)
        - State indicator (Running/Paused)
        
    Bindings:
        - Time updates from state.current_time_display
        - Type updates from state.current_type_display
        - Progress updates from state.progress_percentage
        
    Refresh Trigger:
        - ui.timer calls timer_display.refresh() every 1 second
    """
    ...
```

### Control Buttons Component

**Module**: `pomodoro_timer.ui.components.controls`

```python
def control_buttons(state: AppState) -> None:
    """Display timer control buttons.
    
    Args:
        state: Application state to control
        
    Buttons:
        - Start Work (visible when idle)
        - Start Break (visible when idle)
        - Pause (visible when running)
        - Resume (visible when paused)
        - Cancel (visible when running or paused)
        
    Button State:
        - Disabled when action not valid for current state
        - Enabled when action valid
        - Icon changes based on state (play/pause/stop)
        
    Actions:
        - Start Work -> await state.start_work()
        - Start Break -> await state.start_break()
        - Pause -> state.pause()
        - Resume -> await state.resume()
        - Cancel -> state.cancel()
        
    Error Handling:
        - Catch SessionAlreadyActive -> show error notification
        - Catch InvalidStateTransition -> show error notification
    """
    ...
```

### Session History Component

**Module**: `pomodoro_timer.ui.components.history`

```python
@ui.refreshable
def session_history(state: AppState) -> None:
    """Display session history table.
    
    Args:
        state: Application state containing history
        
    UI Elements:
        - Table with columns: Type, Date, Time Range, Duration
        - Grouped by date (most recent first)
        - Load more button (pagination)
        - Clear history button (with confirmation)
        
    Data Source:
        - state.history (ObservableList)
        - Automatically refreshes when history changes
        
    Table Columns:
        - Type: "Work" or "Break" with icon
        - Date: "Oct 17, 2025" format
        - Time: "14:30 - 14:55" format
        - Duration: "25 min" format
        
    Actions:
        - Load More -> state.load_history(limit=100, offset=current_count)
        - Clear History -> Confirmation dialog -> state.clear_history()
        
    Pagination:
        - Initially load 50 sessions
        - "Load More" button loads next 50
        - Hide button when no more sessions
    """
    ...
```

### Settings Form Component

**Module**: `pomodoro_timer.ui.components.settings`

```python
def settings_form(state: AppState) -> None:
    """Display settings configuration form.
    
    Args:
        state: Application state containing config
        
    Form Fields:
        - Work Duration (number input, 1-999 minutes)
        - Short Break Duration (number input, 1-999 minutes)
        - Long Break Duration (number input, 1-999 minutes, disabled)
        - Theme (select: Auto/Light/Dark)
        
    Validation:
        - Real-time validation on input
        - Error messages below invalid fields
        - Save button disabled if any field invalid
        
    Actions:
        - Save -> Validate -> state.save_config(config) -> Success notification
        - Cancel -> Reload -> state.load_config()
        - Reset to Defaults -> TimerConfig.default() -> Update form
        
    Error Handling:
        - ValueError -> Show inline error
        - OSError -> Show notification "Cannot save config"
        
    Notes:
        - Long Break field disabled (not yet implemented)
        - Changes apply to NEW sessions only (not current session)
    """
    ...
```

## Database Contract

**Module**: `pomodoro_timer.ui.database`

```python
class SessionDatabase:
    """Manages SQLite database for session history."""
    
    def __init__(self, db_path: Path):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
            
        Postconditions:
            - Database file created if not exists
            - Schema initialized (sessions table, indexes)
            - Connection ready for queries
        """
        ...
    
    def insert_session(self, session: CompletedSession) -> int:
        """Insert completed session into database.
        
        Args:
            session: Completed session to insert
            
        Returns:
            Database-generated ID for inserted session
            
        Raises:
            sqlite3.IntegrityError: If constraint violated
        """
        ...
    
    def get_all_sessions(self, limit: int = 100, offset: int = 0) -> list[CompletedSession]:
        """Get all sessions with pagination.
        
        Args:
            limit: Maximum sessions to return
            offset: Number of sessions to skip
            
        Returns:
            List of sessions, most recent first
        """
        ...
    
    def get_sessions_by_date(self, date: datetime.date) -> list[CompletedSession]:
        """Get sessions for specific date.
        
        Args:
            date: Date to filter by
            
        Returns:
            List of sessions starting on that date, ordered by start_time
        """
        ...
    
    def get_session_count(self) -> int:
        """Get total number of sessions in database.
        
        Returns:
            Count of all sessions
        """
        ...
    
    def clear_all_sessions(self) -> None:
        """Delete all sessions from database.
        
        Warning:
            This is destructive and cannot be undone.
        """
        ...
    
    def close(self) -> None:
        """Close database connection.
        
        Should be called on application shutdown.
        """
        ...
```

## Configuration Contract

**Module**: `pomodoro_timer.ui.config`

```python
class ConfigManager:
    """Manages TOML configuration file."""
    
    def __init__(self, config_path: Path):
        """Initialize config manager.
        
        Args:
            config_path: Path to config.toml file
        """
        ...
    
    def load(self) -> TimerConfig:
        """Load configuration from file.
        
        Returns:
            TimerConfig with user settings, or defaults if file missing
            
        Side Effects:
            - Creates default config file if missing
            - Logs warning if file corrupted
        """
        ...
    
    def save(self, config: TimerConfig) -> None:
        """Save configuration to file.
        
        Args:
            config: Configuration to save
            
        Raises:
            ValueError: If config invalid
            OSError: If file cannot be written
        """
        ...
    
    def reset_to_defaults(self) -> TimerConfig:
        """Reset config to default values.
        
        Returns:
            Default TimerConfig
            
        Side Effects:
            - Overwrites existing config file with defaults
        """
        ...
```

## Keyboard Shortcuts Contract

**Module**: `pomodoro_timer.ui.keyboard`

```python
def setup_keyboard_shortcuts(state: AppState) -> None:
    """Register global keyboard shortcuts.
    
    Args:
        state: Application state to control
        
    Shortcuts:
        - Space: Start (if idle) / Pause (if running) / Resume (if paused)
        - Escape: Cancel (if running or paused)
        - W: Start work session (if idle)
        - B: Start break session (if idle)
        - Ctrl+H: Toggle history visibility
        - Ctrl+,: Open settings dialog
        
    Behavior:
        - Shortcuts work on any page
        - Shortcuts disabled when input field focused
        - Visual feedback on shortcut press (brief highlight)
        
    Implementation:
        Uses ui.keyboard() with event handler checking key codes
    """
    ...
```

## Testing Contract

### Unit Test Fixtures

```python
import pytest
from pomodoro_timer.ui.state import AppState
from pomodoro_timer.ui.models import TimerConfig

@pytest.fixture
def app_state() -> AppState:
    """Create AppState with default configuration for testing.
    
    Returns:
        Fresh AppState instance with in-memory database
    """
    ...

@pytest.fixture
def completed_sessions() -> list[CompletedSession]:
    """Create sample completed sessions for testing.
    
    Returns:
        List of 10 completed sessions with varied dates/types
    """
    ...

@pytest.fixture
def timer_config() -> TimerConfig:
    """Create sample timer configuration for testing.
    
    Returns:
        TimerConfig with custom durations
    """
    ...
```

### UI Test Patterns (Using `user` Fixture)

```python
from nicegui.testing import User

async def test_start_work_session(user: User, app_state: AppState):
    """Test starting a work session via UI.
    
    Acceptance Criteria:
        Given the UI is open with no timer running
        When a user clicks the "Start Work" button
        Then a new Pomodoro work session begins counting down
    """
    await user.open('/')
    await user.should_see('00:00')  # Idle state
    user.find('Start Work').click()
    await user.should_see('25:00')  # Work session started
    assert app_state.is_running
    assert app_state.session.session_type == SessionType.WORK
```

## Contract Validation

### Type Checking

All contracts must pass `ty` type checking:

```bash
uv run ty check src/pomodoro_timer/ui/
```

### Interface Tests

Each contract should have interface tests verifying:
1. All public methods exist
2. Method signatures match contracts
3. Return types are correct
4. Exceptions raised as documented

### Contract Documentation

All contract methods must have:
- Docstring with Args, Returns, Raises sections
- Type hints on all parameters and returns
- Preconditions and Postconditions documented
- Side effects documented

## Versioning

**Current Version**: 1.0.0 (initial contracts)

**Compatibility Promise**:
- Patch versions (1.0.x): Bug fixes, no breaking changes
- Minor versions (1.x.0): New features, backward compatible
- Major versions (x.0.0): Breaking changes allowed

**Deprecation Policy**:
- Methods marked `@deprecated` for one minor version before removal
- Deprecation warnings logged at runtime
- Alternative method suggested in deprecation message
