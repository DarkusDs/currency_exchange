
CURRENCY_DISPLAY_NAMES = {
        "USD": "Долар США",
        "EUR": "Євро",
        "GBP": "Фунт стерлінгів",
        "CHF": "Швейцарський франк",
        "PLN": "Злотий",
        "CZK": "Чеська крона",
    }

def get_display_name(code: str | None, fallback: str) -> str:
    if not code:
        return fallback
    return CURRENCY_DISPLAY_NAMES.get(code, fallback)
