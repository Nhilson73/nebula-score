class NebulaScoreError(Exception):
    """Base exception for Nebula Score domain errors."""


class MethodologyNotFoundError(NebulaScoreError):
    """Raised when a methodology or product is not supported."""


class ValidationError(NebulaScoreError):
    """Raised when input data fails validation."""


class CalculationError(NebulaScoreError):
    """Raised when a score calculation cannot be completed."""
