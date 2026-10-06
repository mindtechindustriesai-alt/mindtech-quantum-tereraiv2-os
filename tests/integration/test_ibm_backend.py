"""Integration tests for IBM backend status."""

import pytest
from mqos.orchestration.backends import get_backend_status, list_available_backends


def test_backend_status_returns_dict():
    status = get_backend_status()
    assert isinstance(status, dict)
    assert "qiskit_aer" in status


def test_list_available_backends_nonempty():
    backends = list_available_backends()
    assert isinstance(backends, list)
    assert len(backends) >= 1
