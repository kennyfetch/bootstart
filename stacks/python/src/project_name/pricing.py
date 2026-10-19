"""Price calculations.

Example module showing the project conventions: units in names, docstrings on public functions,
validation at the boundary, explicit errors. Delete it once real code exists.
"""

PERCENT_BASE = 100


def apply_discount(price_cents: int, discount_percent: int) -> int:
    """Return the price after a percentage discount, rounded half up to the cent.

    Args:
        price_cents: Original price in cents, zero or positive.
        discount_percent: Discount between 0 and 100 inclusive.

    Raises:
        ValueError: If an argument is out of range.
    """
    if price_cents < 0:
        raise ValueError(f"price_cents must be >= 0, got {price_cents}")
    if not 0 <= discount_percent <= PERCENT_BASE:
        raise ValueError(f"discount_percent must be between 0 and 100, got {discount_percent}")

    # Integer math: floats cannot represent most cent amounts exactly.
    # Adding half the divisor before the floor division rounds half up.
    remaining_percent = PERCENT_BASE - discount_percent
    return (price_cents * remaining_percent + PERCENT_BASE // 2) // PERCENT_BASE
