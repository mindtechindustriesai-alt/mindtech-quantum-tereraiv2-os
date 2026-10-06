"""Custom exception types for MQOS TERERAI."""


class MQOSError(Exception):
    """Base exception for all MQOS errors."""


class QuantumBackendError(MQOSError):
    """Raised when a quantum backend fails."""


class NoBackendAvailableError(QuantumBackendError):
    """Raised when no backend can serve a request."""


class AuthenticationError(MQOSError):
    """Raised when authentication fails."""


class InvalidCircuitError(MQOSError):
    """Raised when a circuit is malformed."""


class KeyManagementError(MQOSError):
    """Raised when key operations fail."""
