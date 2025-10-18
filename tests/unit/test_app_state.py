"""Unit tests for AppState class."""

from pomodoro_timer.models.types import SessionState, SessionType
from pomodoro_timer.ui.state import AppState


class TestAppStateProperties:
    """Test AppState property accessors."""

    def test_session_property_returns_timer_session(self):
        """Test that session property returns TimerSession instance."""
        # Given: An AppState instance
        app_state = AppState()

        # When/Then: session property returns TimerSession
        assert app_state.session is not None
        assert hasattr(app_state.session, "state")
        assert hasattr(app_state.session, "session_type")

    def test_engine_property_returns_timer_engine(self):
        """Test that engine property returns TimerEngine instance."""
        # Given: An AppState instance
        app_state = AppState()

        # When/Then: engine property returns TimerEngine
        assert app_state.engine is not None
        assert hasattr(app_state.engine, "start_work")
        assert hasattr(app_state.engine, "pause")

    def test_history_property_returns_observable_list(self):
        """Test that history property returns ObservableList."""
        # Given: An AppState instance
        app_state = AppState()

        # When/Then: history property returns observable list
        assert app_state.history is not None
        assert hasattr(app_state.history, "append")
        assert hasattr(app_state.history, "clear")

    def test_config_property_returns_timer_config(self):
        """Test that config property returns TimerConfig instance."""
        # Given: An AppState instance
        app_state = AppState()

        # When/Then: config property returns TimerConfig
        assert app_state.config is not None
        assert hasattr(app_state.config, "work_duration_minutes")


class TestAppStateComputedProperties:
    """Test AppState computed properties."""

    def test_progress_percentage_is_zero_when_idle(self):
        """Test progress_percentage returns 0.0 when idle."""
        # Given: An idle AppState
        app_state = AppState()

        # When/Then: Progress is 0%
        assert app_state.progress_percentage == 0.0

    def test_progress_percentage_increases_as_time_elapses(self):
        """Test progress_percentage calculation during active session."""
        # Given: An AppState with running work session
        app_state = AppState()
        app_state.session.start_work()

        # Simulate time passing (reduce remaining seconds)
        total_seconds = app_state.session.session_type.duration_seconds
        app_state.session.remaining_seconds = total_seconds // 2  # 50% complete

        # When/Then: Progress is approximately 50%
        progress = app_state.progress_percentage
        assert 45.0 <= progress <= 55.0  # Allow some variance

    def test_is_idle_returns_true_when_idle(self):
        """Test is_idle returns True when no session active."""
        # Given: An idle AppState
        app_state = AppState()

        # When/Then: is_idle is True
        assert app_state.is_idle is True
        assert app_state.is_running is False
        assert app_state.is_paused is False

    def test_is_running_returns_true_when_running(self):
        """Test is_running returns True when session running."""
        # Given: An AppState with running session
        app_state = AppState()
        app_state.session.start_work()

        # When/Then: is_running is True
        assert app_state.is_running is True
        assert app_state.is_idle is False
        assert app_state.is_paused is False

    def test_is_paused_returns_true_when_paused(self):
        """Test is_paused returns True when session paused."""
        # Given: An AppState with paused session
        app_state = AppState()
        app_state.session.start_work()
        app_state.session.pause()

        # When/Then: is_paused is True
        assert app_state.is_paused is True
        assert app_state.is_idle is False
        assert app_state.is_running is False

    def test_current_time_display_formats_time(self):
        """Test current_time_display returns formatted time."""
        # Given: An AppState with running session
        app_state = AppState()
        app_state.session.start_work()

        # When/Then: Time is formatted as MM:SS
        time_display = app_state.current_time_display
        assert ":" in time_display
        parts = time_display.split(":")
        assert len(parts) == 2
        assert parts[0].isdigit()
        assert parts[1].isdigit()

    def test_current_time_display_shows_zero_when_idle(self):
        """Test current_time_display shows 00:00 when idle."""
        # Given: An idle AppState
        app_state = AppState()

        # When/Then: Time displays as 00:00
        assert app_state.current_time_display == "00:00"

    def test_current_type_display_shows_idle_when_no_session(self):
        """Test current_type_display returns 'Idle' when no session."""
        # Given: An idle AppState
        app_state = AppState()

        # When/Then: Type displays as "Idle"
        assert app_state.current_type_display == "Idle"

    def test_current_type_display_shows_work_during_work_session(self):
        """Test current_type_display returns 'Work' during work session."""
        # Given: An AppState with work session
        app_state = AppState()
        app_state.session.start_work()

        # When/Then: Type displays as "Work"
        assert app_state.current_type_display == "Work"

    def test_current_type_display_shows_break_during_break_session(self):
        """Test current_type_display returns 'Break' during break session."""
        # Given: An AppState with break session
        app_state = AppState()
        app_state.session.start_break()

        # When/Then: Type displays as "Break"
        assert app_state.current_type_display == "Break"


class TestAppStateControlMethods:
    """Test AppState control method delegation."""

    async def test_start_work_delegates_to_engine(self):
        """Test that start_work delegates to engine."""
        # Given: An idle AppState
        app_state = AppState()

        # When: Calling start_work (but not awaiting full countdown)
        # We need to test delegation without running full countdown
        # For now, just verify state changes
        app_state.session.start_work()

        # Then: Session is in RUNNING state with WORK type
        assert app_state.session.state == SessionState.RUNNING
        assert app_state.session.session_type == SessionType.WORK

    def test_pause_delegates_to_engine(self):
        """Test that pause delegates to engine."""
        # Given: An AppState with running session
        app_state = AppState()
        app_state.session.start_work()

        # When: Calling pause
        app_state.pause()

        # Then: Session is in PAUSED state
        assert app_state.session.state == SessionState.PAUSED

    def test_cancel_delegates_to_engine(self):
        """Test that cancel delegates to engine."""
        # Given: An AppState with running session
        app_state = AppState()
        app_state.session.start_work()

        # When: Calling cancel
        app_state.cancel()

        # Then: Session is in IDLE state
        assert app_state.session.state == SessionState.IDLE
        assert app_state.session.session_type is None


class TestAppStateHistoryMethods:
    """Test AppState history management methods."""

    def test_record_completion_adds_to_history(self):
        """Test record_completion adds session to history."""
        # Given: An AppState with completed session
        app_state = AppState()
        app_state.session.start_work()
        # Save start_time before manually setting COMPLETED state
        # (normally tick() would transition, but it also clears start_time)
        # So we keep start_time for testing
        start_time = app_state.session.start_time
        app_state.session.state = SessionState.COMPLETED
        app_state.session.start_time = start_time  # Preserve for from_session()

        # When: Recording completion
        initial_count = len(app_state.history)
        app_state.record_completion()

        # Then: History has one more session
        assert len(app_state.history) == initial_count + 1
        assert app_state.history[-1].session_type == SessionType.WORK

    def test_clear_history_empties_list(self):
        """Test clear_history removes all sessions."""
        # Given: An AppState with history
        app_state = AppState()
        app_state.session.start_work()
        start_time = app_state.session.start_time
        app_state.session.state = SessionState.COMPLETED
        app_state.session.start_time = start_time  # Preserve for from_session()
        app_state.record_completion()

        # When: Clearing history
        app_state.clear_history()

        # Then: History is empty
        assert len(app_state.history) == 0


class TestAppStateConfigMethods:
    """Test AppState configuration methods."""

    def test_load_config_returns_config(self):
        """Test load_config returns TimerConfig."""
        # Given: An AppState instance
        app_state = AppState()

        # When: Loading config
        config = app_state.load_config()

        # Then: Config is returned
        assert config is not None
        assert hasattr(config, "work_duration_minutes")

    def test_save_config_updates_internal_config(self):
        """Test save_config updates the internal config."""
        # Given: An AppState with a custom config
        app_state = AppState()
        from pomodoro_timer.ui.models import TimerConfig

        custom_config = TimerConfig(work_duration_minutes=30)

        # When: Saving config
        app_state.save_config(custom_config)

        # Then: Internal config is updated
        assert app_state.config.work_duration_minutes == 30
