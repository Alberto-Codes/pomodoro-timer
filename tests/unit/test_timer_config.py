"""Unit tests for TimerConfig model."""

import pytest

from pomodoro_timer.ui.models import (
    DEFAULT_LONG_BREAK_DURATION,
    DEFAULT_SHORT_BREAK_DURATION,
    DEFAULT_WORK_DURATION,
    MAX_DURATION,
    MIN_DURATION,
    TimerConfig,
)


class TestTimerConfigDefaults:
    """Test TimerConfig default values."""
    
    def test_default_factory_creates_config_with_defaults(self):
        """Test default() factory method creates config with default values."""
        # When: Creating config with default() factory
        config = TimerConfig.default()
        
        # Then: All fields have expected default values
        assert config.work_duration_minutes == DEFAULT_WORK_DURATION
        assert config.short_break_minutes == DEFAULT_SHORT_BREAK_DURATION
        assert config.long_break_minutes == DEFAULT_LONG_BREAK_DURATION
        assert config.theme == "auto"
    
    def test_config_creation_without_args_uses_defaults(self):
        """Test creating TimerConfig without args uses default values."""
        # When: Creating config without arguments
        config = TimerConfig()
        
        # Then: Default values are applied
        assert config.work_duration_minutes == 25
        assert config.short_break_minutes == 5
        assert config.long_break_minutes == 15
        assert config.theme == "auto"
    
    def test_config_creation_with_custom_values(self):
        """Test creating TimerConfig with custom values."""
        # When: Creating config with custom values
        config = TimerConfig(
            work_duration_minutes=30,
            short_break_minutes=10,
            long_break_minutes=20,
            theme="dark",
        )
        
        # Then: Custom values are set
        assert config.work_duration_minutes == 30
        assert config.short_break_minutes == 10
        assert config.long_break_minutes == 20
        assert config.theme == "dark"


class TestTimerConfigValidation:
    """Test TimerConfig validation rules."""
    
    def test_work_duration_below_minimum_raises_error(self):
        """Test that work duration below MIN_DURATION raises ValueError."""
        # When/Then: Creating config with 0 minutes raises error
        with pytest.raises(ValueError, match="work_duration_minutes must be between"):
            TimerConfig(work_duration_minutes=0)
    
    def test_work_duration_above_maximum_raises_error(self):
        """Test that work duration above MAX_DURATION raises ValueError."""
        # When/Then: Creating config with 1000 minutes raises error
        with pytest.raises(ValueError, match="work_duration_minutes must be between"):
            TimerConfig(work_duration_minutes=1000)
    
    def test_work_duration_at_minimum_is_valid(self):
        """Test that work duration at MIN_DURATION is valid."""
        # When: Creating config with minimum duration
        config = TimerConfig(work_duration_minutes=MIN_DURATION)
        
        # Then: Config is created successfully
        assert config.work_duration_minutes == MIN_DURATION
    
    def test_work_duration_at_maximum_is_valid(self):
        """Test that work duration at MAX_DURATION is valid."""
        # When: Creating config with maximum duration
        config = TimerConfig(work_duration_minutes=MAX_DURATION)
        
        # Then: Config is created successfully
        assert config.work_duration_minutes == MAX_DURATION
    
    def test_short_break_below_minimum_raises_error(self):
        """Test that short break below MIN_DURATION raises ValueError."""
        # When/Then: Creating config with invalid short break raises error
        with pytest.raises(ValueError, match="short_break_minutes must be between"):
            TimerConfig(short_break_minutes=0)
    
    def test_short_break_above_maximum_raises_error(self):
        """Test that short break above MAX_DURATION raises ValueError."""
        # When/Then: Creating config with invalid short break raises error
        with pytest.raises(ValueError, match="short_break_minutes must be between"):
            TimerConfig(short_break_minutes=1000)
    
    def test_long_break_below_minimum_raises_error(self):
        """Test that long break below MIN_DURATION raises ValueError."""
        # When/Then: Creating config with invalid long break raises error
        with pytest.raises(ValueError, match="long_break_minutes must be between"):
            TimerConfig(long_break_minutes=0)
    
    def test_long_break_above_maximum_raises_error(self):
        """Test that long break above MAX_DURATION raises ValueError."""
        # When/Then: Creating config with invalid long break raises error
        with pytest.raises(ValueError, match="long_break_minutes must be between"):
            TimerConfig(long_break_minutes=1000)
    
    def test_invalid_theme_raises_error(self):
        """Test that invalid theme value raises ValueError."""
        # When/Then: Creating config with invalid theme raises error
        with pytest.raises(ValueError, match="theme must be 'auto', 'light', or 'dark'"):
            TimerConfig(theme="invalid")
    
    def test_valid_theme_auto(self):
        """Test that 'auto' theme is valid."""
        # When: Creating config with 'auto' theme
        config = TimerConfig(theme="auto")
        
        # Then: Config is created successfully
        assert config.theme == "auto"
    
    def test_valid_theme_light(self):
        """Test that 'light' theme is valid."""
        # When: Creating config with 'light' theme
        config = TimerConfig(theme="light")
        
        # Then: Config is created successfully
        assert config.theme == "light"
    
    def test_valid_theme_dark(self):
        """Test that 'dark' theme is valid."""
        # When: Creating config with 'dark' theme
        config = TimerConfig(theme="dark")
        
        # Then: Config is created successfully
        assert config.theme == "dark"
    
    def test_negative_work_duration_raises_error(self):
        """Test that negative work duration raises ValueError."""
        # When/Then: Creating config with negative duration raises error
        with pytest.raises(ValueError, match="work_duration_minutes must be between"):
            TimerConfig(work_duration_minutes=-1)
    
    def test_all_durations_at_boundary_values(self):
        """Test config with all durations at valid boundaries."""
        # When: Creating config with all durations at MIN_DURATION
        config = TimerConfig(
            work_duration_minutes=MIN_DURATION,
            short_break_minutes=MIN_DURATION,
            long_break_minutes=MIN_DURATION,
        )
        
        # Then: Config is created successfully
        assert config.work_duration_minutes == MIN_DURATION
        assert config.short_break_minutes == MIN_DURATION
        assert config.long_break_minutes == MIN_DURATION


class TestTimerConfigConstants:
    """Test that configuration constants have expected values."""
    
    def test_default_work_duration(self):
        """Test default work duration is 25 minutes."""
        assert DEFAULT_WORK_DURATION == 25
    
    def test_default_short_break_duration(self):
        """Test default short break duration is 5 minutes."""
        assert DEFAULT_SHORT_BREAK_DURATION == 5
    
    def test_default_long_break_duration(self):
        """Test default long break duration is 15 minutes."""
        assert DEFAULT_LONG_BREAK_DURATION == 15
    
    def test_min_duration(self):
        """Test minimum duration is 1 minute."""
        assert MIN_DURATION == 1
    
    def test_max_duration(self):
        """Test maximum duration is 999 minutes."""
        assert MAX_DURATION == 999
