"""Unit tests for backend routing."""

from mqos.orchestration.router import select_backend, route_circuit


def test_select_backend_returns_string():
    backend = select_backend(circuit_qubits=2, prefer_hardware=False)
    assert isinstance(backend, str)


def test_route_circuit_has_rationale():
    result = route_circuit(circuit_qubits=2, shots=1024, prefer_hardware=False)
    assert "selected_backend" in result
    assert "rationale" in result
