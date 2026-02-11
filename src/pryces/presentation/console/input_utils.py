def validate_symbol(value: str) -> bool:
    return bool(value and value.strip() and len(value.strip()) <= 10)


def validate_symbols(value: str) -> bool:
    if not value or not value.strip():
        return False

    symbols = [s.strip() for s in value.split(",")]
    return all(symbol and len(symbol) <= 10 for symbol in symbols)


def validate_positive_integer(value: str) -> bool:
    try:
        return int(value) > 0
    except (ValueError, TypeError):
        return False


def parse_symbols_input(value: str) -> list[str]:
    symbols = [s.strip().upper() for s in value.split(",")]
    return [s for s in symbols if s]
