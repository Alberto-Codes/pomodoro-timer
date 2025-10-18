"""Configuration management for timer settings.

This module provides TOML-based configuration persistence for user settings.
"""

import tomllib
from pathlib import Path

import tomli_w

from pomodoro_timer.ui.models import TimerConfig


class ConfigManager:
    """Manages timer configuration persistence using TOML files.

    Attributes:
        config_path: Path to the configuration file
    """

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize configuration manager.

        Args:
            config_path: Path to config file. If None, uses default location:
                        ~/.config/pomodoro-timer/config.toml
        """
        if config_path is None:
            # Use XDG Base Directory specification
            config_dir = Path.home() / ".config" / "pomodoro-timer"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_path = config_dir / "config.toml"

        self.config_path = config_path

    def load(self) -> TimerConfig:
        """Load configuration from TOML file.

        Returns:
            TimerConfig object with loaded settings, or default config if file doesn't exist
        """
        if not self.config_path.exists():
            # Create default config if it doesn't exist
            default_config = TimerConfig.default()
            self.save(default_config)
            return default_config

        with open(self.config_path, "rb") as f:
            config_dict = tomllib.load(f)

        return TimerConfig(
            work_duration_minutes=config_dict["timer"]["work_duration_minutes"],
            short_break_minutes=config_dict["timer"]["short_break_minutes"],
            long_break_minutes=config_dict["timer"]["long_break_minutes"],
            theme=config_dict["ui"]["theme"],
        )

    def save(self, config: TimerConfig) -> None:
        """Save configuration to TOML file.

        Args:
            config: The TimerConfig to save

        Raises:
            ValueError: If config validation fails
        """
        # Ensure parent directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        config_dict = {
            "timer": {
                "work_duration_minutes": config.work_duration_minutes,
                "short_break_minutes": config.short_break_minutes,
                "long_break_minutes": config.long_break_minutes,
            },
            "ui": {
                "theme": config.theme,
            },
        }

        with open(self.config_path, "wb") as f:
            tomli_w.dump(config_dict, f)

    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        default_config = TimerConfig.default()
        self.save(default_config)
