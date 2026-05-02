import re

from playwright.sync_api import Locator


def extract_item_url(result_item: Locator) -> str | None:
    item_link = result_item.locator("a.s-item__link[href^='http']").first
    href = item_link.get_attribute("href")
    if not href or "ebay.com/itm/" not in href:
        return None
    return href


def extract_item_price(result_item: Locator) -> float | None:
    price_text = result_item.locator(".s-item__price").first.inner_text(timeout=1_000)
    match = re.search(r"\d[\d,]*(?:\.\d+)?", price_text.replace("\xa0", " "))
    if not match:
        return None

    try:
        return float(match.group(0).replace(",", ""))
    except ValueError:
        return None
