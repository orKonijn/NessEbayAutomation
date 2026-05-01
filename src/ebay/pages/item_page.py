import random
import re
from pathlib import Path

from playwright.sync_api import (
    Error,
    Locator,
    Page,
    TimeoutError as PlaywrightTimeoutError,
    expect,
)

from ebay.utils.log import log_item_result
from ebay.utils.place_holder import is_placeholder_value
from ebay.utils.random_option import pick_random_option_from_container


def select_random_available_option(select: Locator) -> str | None:
    options = select.locator("option")
    available_options: list[tuple[str, str]] = []

    for index in range(options.count()):
        option = options.nth(index)

        value = (option.get_attribute("value") or "").strip()
        label = (option.inner_text(timeout=1000) or "").strip()

        if option.is_disabled() or not value or is_placeholder_value(label):
            continue

        available_options.append((value, label))

    if not available_options:
        return None

    value, label = random.choice(available_options)
    select.select_option(value=value)

    return f"select:{label}"


class ItemPage:
    """eBay item detail page interactions."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.screenshot_dir = Path("artifacts/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def add_items_to_cart(self, urls: list[str]) -> None:
        for index, url in enumerate(urls, start=1):
            self._process_item(index=index, url=url)

    def _process_item(self, index: int, url: str) -> None:
        selected_variants: list[str] = []
        success = False
        error_message: str | None = None

        try:
            self.page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            self._wait_for_item_page()
            selected_variants = self._select_variants()
            success = self._click_add_to_cart()

        except Exception as exc:
            error_message = str(exc)

        finally:
            screenshot_path = self._save_screenshot(index, success)

            log_item_result(
                index=index,
                url=url,
                selected_variants=selected_variants,
                success=success,
                error_message=error_message,
                screenshot_path=str(screenshot_path) if screenshot_path else None,
            )

    def _wait_for_item_page(self) -> None:
        item_content = self.page.locator(
            "[data-testid='x-item-title'], "
            "[data-test-id='x-item-title'], "
            "#CenterPanelInternal, "
            "main"
        ).first

        expect(item_content).to_be_visible(timeout=20_000)

    def _select_variants(self) -> list[str]:
        selections: list[str] = []

        selections.extend(self._select_dropdown_variants())
        selections.extend(self._select_clickable_variants())

        return selections

    def _select_dropdown_variants(self) -> list[str]:
        selections: list[str] = []

        dropdowns = self.page.locator("select")

        for index in range(dropdowns.count()):
            dropdown = dropdowns.nth(index)

            if not dropdown.is_visible() or dropdown.is_disabled():
                continue

            selected = select_random_available_option(dropdown)

            if selected:
                selections.append(selected)

        return selections

    def _select_clickable_variants(self) -> list[str]:
        selections: list[str] = []

        variant_containers = self.page.locator(
            "fieldset, "
            "[role='listbox'], "
            "[data-testid*='variation' i], "
            "[data-test-id*='variation' i]"
        )

        for index in range(variant_containers.count()):
            container = variant_containers.nth(index)

            option = pick_random_option_from_container(container)

            if option is None:
                continue

            locator, label = option
            locator.click()

            if label:
                selections.append(f"option:{label}")

        return selections

    def _click_add_to_cart(self) -> bool:
        button = self.page.get_by_role(
            "button",
            name=re.compile(r"Add to (cart|basket)", re.IGNORECASE),
        )

        if button.count() == 0:
            button = self.page.locator(
                "[data-testid*='add-to-cart' i], "
                "[data-test-id*='add-to-cart' i], "
                "#atcBtn_btn_1"
            )

        expect(button.first).to_be_visible(timeout=10_000)
        button.first.click()

        return self._wait_for_cart_confirmation()

    def _wait_for_cart_confirmation(self) -> bool:
        try:
            self.page.wait_for_url(
                re.compile(r"cart|checkout|viCart", re.IGNORECASE),
                timeout=10_000,
            )
            return True
        except PlaywrightTimeoutError:
            pass

        confirmation = self.page.locator(
            "text=/added to (your )?(cart|basket)/i, "
            "[role='dialog'], "
            "[aria-live='polite']"
        ).first

        try:
            expect(confirmation).to_be_visible(timeout=8_000)
            return True
        except Error:
            return False

    def _save_screenshot(self, index: int, success: bool) -> str:
        status = "success" if success else "failed"
        screenshot_path = self.screenshot_dir / f"add-to-cart-item-{index}-{status}.png"

        try:
            self.page.screenshot(path=str(screenshot_path), full_page=True)
            return str(screenshot_path)
        except Error:
            return ""
