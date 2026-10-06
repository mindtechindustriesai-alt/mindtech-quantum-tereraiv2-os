"""Shared pytest fixtures."""

import pytest


@pytest.fixture
def sample_chsh_angles():
    return [(0, 22.5), (0, 67.5), (45, 22.5), (45, 67.5)]
