"""Common quantum gate wrappers for reuse across modules."""

import math
from qiskit import QuantumCircuit


def apply_hadamard(qc: QuantumCircuit, qubit: int) -> None:
    qc.h(qubit)


def apply_cnot(qc: QuantumCircuit, control: int, target: int) -> None:
    qc.cx(control, target)


def apply_ry(qc: QuantumCircuit, angle_deg: float, qubit: int) -> None:
    qc.ry(math.radians(angle_deg), qubit)


def apply_rx(qc: QuantumCircuit, angle_deg: float, qubit: int) -> None:
    qc.rx(math.radians(angle_deg), qubit)


def apply_rz(qc: QuantumCircuit, angle_deg: float, qubit: int) -> None:
    qc.rz(math.radians(angle_deg), qubit)
