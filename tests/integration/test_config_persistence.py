"""Integration tests for configuration persistence."""

import pytest

from pomodoro_timer.models.types import SessionType
from pomodoro_timer.ui.config import ConfigManager
from pomodoro_timer.ui.models import TimerConfig
from pomodoro_timer.ui.state import AppState


class TestConfigPersistence:
    """Test configuration persistence to TOML files."""

    def test_save_and_load_config_preserves_values(self, temp_config_path):
        """Test that saving and loading config preserves all values."""
        # Arrange
        manager = ConfigManager(temp_config_path)
        custom_config = TimerConfig(
            work_duration_minutes=30,
            short_break_minutes=10,
            long_break_minutes=20,
            theme="dark"
        )
        
        # Act
        manager.save(custom_config)
        loaded_config = manager.load()
        
        # Assert
        assert loaded_config.work_duration_minutes == 30
        assert loaded_config.short_break_minutes == 10
        assert loaded_config.long_break_minutes == 20
        assert loaded_config.theme == "dark"

    def test_load_creates_default_config_if_missing(self, temp_config_path):
        """Test that load creates default config if file doesn't exist."""
        # Arrange
        manager = ConfigManager(temp_config_path)
        # Ensure file doesn't exist
        if temp_config_path.exists():
            temp_config_path.unlink()
        
        # Act
        config = manager.load()
        
        # Assert - Should return defaults
        assert config.work_duration_minutes == 25
        assert config.short_break_minutes == 5
        assert config.long_break_minutes == 15
        assert temp_config_path.exists()


class TestConfigValidation:
    """Test configuration validation."""

    def test_config_rejects_zero_duration(self):
        """Test that zero duration is rejected."""
        # Act & Assert
        with pytest.raises(ValueError, match="must be between"):
            TimerConfig(
                work_duration_minutes=0,
                short_break_minutes=5,
                long_break_minutes=15
            )

    def test_config_rejects_negative_duration(self):
        """Test that negative duration is rejected."""
        # Act & Assert
        with pytest.raises(ValueError, match="must be between"):
            TimerConfig(
                work_duration_minutes=-5,
                short_break_minutes=5,
                long_break_minutes=15
            )

    def test_config_rejects_duration_above_max(self):
        """Test that duration above maximum is rejected."""
        # Act & Assert
        with pytest.raises(ValueError, match="must be between"):
            TimerConfig(
                work_duration_minutes=1000,  # Max is 999
                short_break_minutes=5,
                long_break_minutes=15
            )

    def test_config_accepts_valid_duration(self):
        """Test that valid durations are accepted."""
        # Act
        config = TimerConfig(
            work_duration_minutes=30,
            short_break_minutes=10,
            long_break_minutes=20
        )
        
        # Assert
        assert config.work_duration_minutes == 30
        assert config.short_break_minutes == 10


class TestConfigApplication:
    """Test applying configuration to SessionType."""

    def test_apply_config_updates_session_type_durations(self):
        """Test that applying config updates SessionType duration_seconds."""
        # Arrange
        from pomodoro_timer.models.types import SessionDurations
        
        app_state = AppState()
        custom_config = TimerConfig(
            work_duration_minutes=30,
            short_break_minutes=10,
            long_break_minutes=20
        )
        
        # Save original durations
        original_work = SessionDurations.work_duration_seconds
        original_break = SessionDurations.break_duration_seconds
        
        # Act
        app_state.apply_config(custom_config)
        
        # Assert - SessionType durations should be updated
        assert SessionType.WORK.duration_seconds == 30 * 60  # 1800 seconds
        assert SessionType.BREAK.duration_seconds == 10 * 60  # 600 seconds
        
        # Cleanup - restore original durations
        SessionDurations.work_duration_seconds = original_work
        SessionDurations.break_duration_seconds = original_break

    def test_config_persists_across_app_restart(self, temp_config_path):
        """Test that configuration persists when app is restarted."""
        # Arrange - First "app session"
        manager1 = ConfigManager(temp_config_path)
        app_state1 = AppState()
        app_state1._config_manager = manager1
        
        custom_config = TimerConfig(
            work_duration_minutes=30,
            short_break_minutes=10,
            long_break_minutes=20
        )
        app_state1.save_config(custom_config)
        
        # Act - Simulate app restart with new AppState
        manager2 = ConfigManager(temp_config_path)
        app_state2 = AppState()
        app_state2._config_manager = manager2
        loaded_config = app_state2.load_config()
        
        # Assert
        assert loaded_config.work_duration_minutes == 30
        assert loaded_config.short_break_minutes == 10


@pytest.fixture
def temp_config_path(tmp_path):
    """Create a temporary config path for testing."""
    return tmp_path / "test_config.toml"
