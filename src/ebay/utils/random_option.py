import logging
import random

from playwright.sync_api import Locator

from ebay.utils.place_holder import is_placeholder_value

logger = logging.getLogger(__name__)


def pick_random_option_from_container(
    container: Locator,
) -> tuple[Locator, str] | None:
    options = container.locator("[role='option'], " "[role='radio'], " "button")

    available: list[tuple[Locator, str]] = []

    for index in range(options.count()):
        option = options.nth(index)

        if option.is_disabled() or not option.is_visible():
            continue

        label = (
            option.get_attribute("aria-label") or option.inner_text(timeout=1000) or ""
        ).strip()

        if is_placeholder_value(label):
            continue

        available.append((option, label))

    return random.choice(available) if available else None


def select_random_available_option(select: Locator) -> str | None:
    options = select.locator("option")
    available_options: list[tuple[str, str]] = []

    for index in range(options.count()):
        option = options.nth(index)

        value = (option.get_attribute("value") or "").strip()
        label = (option.inner_text(timeout=1_000) or "").strip()

        if option.is_disabled() or not value or is_placeholder_value(label):
            continue

        available_options.append((value, label))

    if not available_options:
        logger.debug("No available dropdown options found.")
        return None

    value, label = random.choice(available_options)
    select.select_option(value=value)

    logger.info("Selected dropdown option | label=%s | value=%s", label, value)

    return f"select:{label}"
