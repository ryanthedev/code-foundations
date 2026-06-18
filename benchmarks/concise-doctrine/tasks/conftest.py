"""pytest configuration for the concise-doctrine task suite."""
import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "slow: marks tests that run AST mutation scoring (deselect with -m 'not slow')",
    )
