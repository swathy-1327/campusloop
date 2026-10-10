import math


def parse_nonnegative_amount(value):
    """Return a finite, non-negative amount, or None for invalid input."""
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return None
    return amount if math.isfinite(amount) and amount >= 0 else None
