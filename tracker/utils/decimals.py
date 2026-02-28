from decimal import Decimal, ROUND_HALF_UP

def quantize_decimal(value: Decimal | float | str, places: int = 2) -> Decimal:
    d = value if isinstance(value, Decimal) else Decimal(str(value))
    step = Decimal("1").scaleb(-places)  # 10^-places
    return d.quantize(step, rounding=ROUND_HALF_UP)