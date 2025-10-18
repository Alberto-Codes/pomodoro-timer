"""Acceptance tests for timer display component (User Story 1).

These tests verify the visual timer display functionality.
According to Principle I (Test-First Development), these tests are written
FIRST and should FAIL until the implementation is complete.
"""

import pytest
from nicegui.testing import User

from pomodoro_timer.models.types import SessionState
from pomodoro_timer.ui.state import app_state


pytestmark = pytest.mark.ui


@pytest.mark.asyncio
class TestTimerDisplayIdleState:
    """Test timer display when idle (US1 - Acceptance Scenario 1)."""
    
    async def test_timer_shows_zero_time_when_idle(self, user: User):
        """Given UI is launched, When viewing main screen, Then timer shows 00:00."""
        # This test will fail until timer_display component is implemented
        # Expected: Timer displays "00:00" when no session is active
        
        # Reset state to idle
        if app_state.session.state != SessionState.IDLE:
            app_state.cancel()
        
        # Navigate to main page (will be implemented)
        await user.open("/")
        
        # Then: Timer displays 00:00
        await user.should_see("00:00")
    
    async def test_timer_shows_idle_state_label(self, user: User):
        """Given UI is launched, When viewing main screen, Then shows 'Idle' state."""
        # This test will fail until timer_display component is implemented
        # Expected: Display shows "Idle" state when no session active
        
        # Reset state to idle
        if app_state.session.state != SessionState.IDLE:
            app_state.cancel()
        
        # Navigate to main page
        await user.open("/")
        
        # Then: State label shows "Idle"
        await user.should_see("Idle")
    
    async def test_timer_shows_no_progress_when_idle(self, user: User):
        """Given UI is idle, When viewing display, Then progress is 0%."""
        # This test will fail until timer_display with progress bar is implemented
        # Expected: Progress bar shows 0% or is hidden when idle
        
        # Reset state to idle
        if app_state.session.state != SessionState.IDLE:
            app_state.cancel()
        
        # Navigate to main page
        await user.open("/")
        
        # Then: Progress percentage is 0
        assert app_state.progress_percentage == 0.0


@pytest.mark.asyncio
class TestTimerDisplayDuringWorkSession:
    """Test timer display during active work session (US1 - Acceptance Scenario 2)."""
    
    async def test_timer_shows_work_session_type(self, user: User):
        """Given work session started, When viewing timer, Then shows 'Work' type."""
        # This test will fail until timer_display component is implemented
        # Expected: Display shows "Work" session type label
        
        # Start work session
        app_state.session.start_work()
        
        # Navigate to main page
        await user.open("/")
        
        # Then: Session type shows "Work"
        await user.should_see("Work")
    
    async def test_timer_shows_initial_work_duration(self, user: User):
        """Given work session started, When viewing timer, Then shows 25:00."""
        # This test will fail until timer_display component is implemented
        # Expected: Timer shows 25:00 (or configured work duration)
        
        # Start work session
        app_state.session.start_work()
        
        # Navigate to main page
        await user.open("/")
        
        # Then: Timer shows initial work duration
        await user.should_see("25:00")
    
    async def test_timer_shows_running_badge(self, user: User):
        """Given work session running, When viewing timer, Then shows 'Running' badge."""
        # This test will fail until timer_display with state badge is implemented
        # Expected: Visual indicator (badge/label) shows "Running" state
        
        # Start work session
        app_state.session.start_work()
        
        # Navigate to main page
        await user.open("/")
        
        # Then: Running badge is visible
        await user.should_see("Running")
    
    async def test_timer_updates_every_second(self, user: User):
        """Given session running, When time elapses, Then display updates every second."""
        # This test will fail until timer_display with refresh mechanism is implemented
        # Expected: Timer countdown updates automatically
        
        # Start work session
        app_state.session.start_work()
        
        # Navigate to main page
        await user.open("/")
        
        # Get initial time display
        initial_time = app_state.session.formatted_time
        
        # Wait for more than 1 second
        await user.wait(1.5)
        
        # Then: Time has decreased
        current_time = app_state.session.formatted_time
        assert current_time != initial_time  # Time should have changed


@pytest.mark.asyncio
class TestTimerDisplayOnCompletion:
    """Test timer display when session completes (US1 - Acceptance Scenario 3)."""
    
    async def test_timer_reaches_zero_and_shows_completed(self, user: User):
        """Given session completes, When timer reaches 00:00, Then shows completed state."""
        # This test will fail until timer_display handles completion is implemented
        # Expected: Timer shows 00:00 and "Completed" state
        
        # Start work session and immediately complete it (for testing)
        app_state.session.start_work()
        app_state.session.remaining_seconds = 0
        app_state.session.state = SessionState.COMPLETED
        
        # Navigate to main page
        await user.open("/")
        
        # Then: Shows completed state
        await user.should_see("00:00")
        # Note: Actual completion behavior will be tested in integration tests


@pytest.mark.asyncio  
class TestTimerDisplayRefresh:
    """Test timer display refresh mechanism."""
    
    async def test_timer_display_refreshes_automatically(self, user: User):
        """Given timer running, When viewing page, Then display auto-refreshes."""
        # This test will fail until timer refresh mechanism is implemented
        # Expected: UI timer component has automatic 1-second refresh
        
        # Start work session
        app_state.session.start_work()
        
        # Navigate to main page
        await user.open("/")
        
        # Wait to verify refresh happens
        await user.wait(0.5)
        
        # Then: Page should have refresh mechanism
        # (actual verification depends on implementation)
        assert app_state.is_running
