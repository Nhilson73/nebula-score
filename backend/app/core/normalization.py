from typing import Any


def clamp(value: float, min_value: float = 0.0, max_value: float = 100.0) -> float:
    """Clamp a numeric value to the inclusive range [min_value, max_value]."""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return min_value
    if numeric < min_value:
        return min_value
    if numeric > max_value:
        return max_value
    return numeric


def linear_clamp(
    value: float,
    in_min: float,
    in_max: float,
    out_min: float = 0.0,
    out_max: float = 100.0,
) -> float:
    """Map a value linearly from one range to another, clamped to the output range."""
    if in_min >= in_max:
        return out_min
    normalized = (clamp(value, in_min, in_max) - in_min) / (in_max - in_min)
    return out_min + normalized * (out_max - out_min)


def round_score(value: float, decimals: int = 1) -> float:
    """Round a score to the configured number of decimals."""
    return round(value, decimals)


def as_number(value: Any) -> float:
    """Safely convert a value to float, defaulting to 0.0 on failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
