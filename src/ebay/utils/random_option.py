import random

from playwright.sync_api import Locator

from ebay.utils.place_holder import is_placeholder_value


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
                option.get_attribute("aria-label")
                or option.inner_text(timeout=1000)
                or ""
        ).strip()

        if is_placeholder_value(label):
            continue

        available.append((option, label))

    return random.choice(available) if available else None