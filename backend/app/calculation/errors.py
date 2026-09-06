class CalculationError(Exception):
    """Base error for deterministic calculations."""


class FormulaNotFoundError(CalculationError):
    """Raised when a requested formula is not registered."""


class UnitConversionError(CalculationError):
    """Raised when units cannot be converted."""


class VerificationError(CalculationError):
    """Raised when a result fails verification."""
