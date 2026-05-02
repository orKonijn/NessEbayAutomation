import re


def parse_price(text: str) -> float | None:
    normalized = text.replace("\u00a0", " ")
    matches = re.findall(
        r"(?:[A-Z]{2}\s*)?\$\s*[\d,]+(?:\.\d{1,2})?|[\d,]+\.\d{2}", normalized
    )
    if not matches:
        return None

    candidate = matches[-1]
    digits_only = re.sub(r"[^\d.]", "", candidate)
    if digits_only.count(".") > 1:
        return None

    try:
        return float(digits_only)
    except ValueError:
        return None
