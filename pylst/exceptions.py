# pylst/exceptions.py
from __future__ import annotations
from typing import Any

__all__ = [
    "PylstError",
    "InvalidMaskError",
    "InputShapesMismatchError",
    "InvalidMethodError",
    "MissingRequiredArgumentError",
    "assert_required_keywords_provided",
]

class PylstError(Exception):
    """Base class for all pylst-specific exceptions."""
    pass

class InvalidMaskError(PylstError):
    """Raised when a mask array is invalid (wrong shape, dtype, etc.)."""
    pass

class InputShapesMismatchError(PylstError, ValueError):
    """Raised when input arrays (bands, masks, etc.) have mismatched shapes."""
    pass

class InvalidMethodError(PylstError, ValueError):
    """Raised when an invalid or unsupported algorithm/method is requested."""
    pass

class MissingRequiredArgumentError(PylstError, TypeError):
    """Raised when a required keyword argument is missing or None."""
    pass

def assert_required_keywords_provided(
    required: list[str] | tuple[str, ...],
    **kwargs: Any,
) -> None:
    """
    Validate that all required keyword arguments are provided and not None.

    Raises MissingRequiredArgumentError if any are missing.
    """
    missing = [kw for kw in required if kw not in kwargs or kwargs[kw] is None]
    if missing:
        raise MissingRequiredArgumentError(
            f"Missing or None required argument(s): {', '.join(missing)}. "
            f"Required: {', '.join(required)}"
        )
