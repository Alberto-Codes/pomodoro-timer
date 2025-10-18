"""Test fixtures for UI acceptance tests.

This module provides shared fixtures for testing NiceGUI components.
"""

import pytest
from nicegui.testing import User


@pytest.fixture
def user() -> User:
    """Create a test user for NiceGUI component testing.
    
    The user fixture is provided by the NiceGUI testing plugin and allows
    simulating user interactions with UI components in tests.
    
    Returns:
        User instance for interacting with UI components in tests
    """
    # The actual user fixture is provided by nicegui.testing.user_plugin
    # This is just a type hint placeholder for documentation
    raise NotImplementedError("This fixture is provided by NiceGUI plugin")
