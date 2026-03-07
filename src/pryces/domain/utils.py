from decimal import Decimal


def _calculate_percentage_change(current: Decimal, reference: Decimal) -> Decimal:
    return (current - reference) / reference * 100
