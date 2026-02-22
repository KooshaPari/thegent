"""Pytest configuration and fixtures for thegent tests."""

import sys
from unittest.mock import MagicMock

# Mock the thegent_fs module before any imports
sys.modules['thegent_fs'] = MagicMock()
