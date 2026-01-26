
CURRENCY_DISPLAY_NAMES = {
        "USD": "Долар США",
        "EUR": "Євро",
        "GBP": "Фунт стерлінгів",
        "CHF": "Швейцарський франк",
        "PLN": "Злотий",
        "CZK": "Чеська крона",
    }

def get_display_name(code: str | None, fallback: str) -> str:
    """
    Returns a human-readable currency name by its code, falling back to the provided name if the code is missing or unknown

    :param code: Optional currency code (e.g. "USD", "EUR")
    :param fallback: Default name used when the currency code is not available
    :return: Localized display name for the currency
    """
    if not code:
        return fallback
    return CURRENCY_DISPLAY_NAMES.get(code, fallback)
