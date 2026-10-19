import pytest

from project_name.pricing import apply_discount


@pytest.mark.parametrize(
    ("price_cents", "discount_percent", "expected_cents"),
    [
        (1000, 0, 1000),
        (1000, 25, 750),
        (1000, 100, 0),
        (999, 50, 500),  # 499.5 rounds half up
    ],
)
def test_apply_discount_returns_discounted_price(
    price_cents: int, discount_percent: int, expected_cents: int
) -> None:
    result = apply_discount(price_cents, discount_percent)

    assert result == expected_cents


def test_apply_discount_rejects_negative_price() -> None:
    with pytest.raises(ValueError, match="price_cents"):
        apply_discount(-1, 10)


@pytest.mark.parametrize("discount_percent", [-1, 101])
def test_apply_discount_rejects_out_of_range_discount(discount_percent: int) -> None:
    with pytest.raises(ValueError, match="discount_percent"):
        apply_discount(1000, discount_percent)
