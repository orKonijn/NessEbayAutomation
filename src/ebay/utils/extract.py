import re
from typing import Optional


def extract_item_url(result_item) -> Optional[str]:
    item_link = result_item.locator(
        "xpath=.//a[contains(@class,'s-item__link') and starts-with(@href,'http')]"
    ).first
    href = item_link.get_attribute("href")
    if not href or "ebay.com/itm/" not in href:
        return None
    return href


def extract_item_price(result_item) -> Optional[float]:
    price_node = result_item.locator(
        "xpath=.//*[contains(@class,'s-item__price')]"
    ).first
    if price_node.count() == 0:
        return None

    price_text = (price_node.inner_text() or "").replace("\xa0", " ").strip()
    if not price_text:
        return None

    # Ignore currency sign/text and parse the first numeric value as-is.
    # Examples: "$1,299.99", "ILS 1,299.99", "₪1,299.99", "US $9.99 to US $19.99"
    match = re.search(r"\d[\d,]*(?:\.\d+)?", price_text)
    if not match:
        return None

    try:
        return float(match.group(0).replace(",", ""))
    except ValueError:
        return None
