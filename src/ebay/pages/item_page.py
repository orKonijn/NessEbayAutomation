import logging
import re
from pathlib import Path

import allure
from playwright.sync_api import (
    Error,
    Page,
    TimeoutError as PlaywrightTimeoutError,
    expect,
)

from ebay.utils.attach_summery import attach_summary
from ebay.utils.log import log_item_result
from ebay.utils.random_option import (
    pick_random_option_from_container,
    select_random_available_option,
)

logger = logging.getLogger(__name__)


class ItemPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.screenshot_dir = Path("artifacts/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    @allure.step("Add items to cart")
    def add_items_to_cart(self, urls: list[str]) -> None:
        allure.attach(
            "\n".join(urls),
            name="Item URLs",
            attachment_type=allure.attachment_type.TEXT,
        )

        logger.info("Adding %d items to cart", len(urls))

        for index, url in enumerate(urls, start=1):
            self._add_single_item(index, url)

    def _add_single_item(self, index: int, url: str) -> None:
        selected_options: list[str] = []
        error_message: str | None = None
        added_to_cart = False

        logger.info("Processing item %d: %s", index, url)

        try:
            self.page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            self._wait_until_loaded()

            selected_options = self._choose_options()
            added_to_cart = self._add_to_cart()

        except (Error, PlaywrightTimeoutError) as exc:
            error_message = str(exc)
            logger.warning("Item %d was not added to cart: %s", index, error_message)

            allure.attach(
                error_message,
                name=f"Item {index} error",
                attachment_type=allure.attachment_type.TEXT,
            )

        screenshot_path = self._save_screenshot(index, added_to_cart)

        attach_summary(
            index=index,
            url=url,
            success=added_to_cart,
            selected_options=selected_options,
            error_message=error_message,
            screenshot_path=screenshot_path,
        )

        log_item_result(
            index=index,
            url=url,
            selected_variants=selected_options,
            success=added_to_cart,
            error_message=error_message,
            screenshot_path=screenshot_path,
        )

    def _wait_until_loaded(self) -> None:
        title = self.page.locator("[data-testid='x-item-title']").first
        expect(title).to_be_visible(timeout=20_000)

    def _choose_options(self) -> list[str]:
        selected: list[str] = []

        selected.extend(self._choose_dropdown_options())
        selected.extend(self._choose_variation_options())

        return selected

    def _choose_dropdown_options(self) -> list[str]:
        selected: list[str] = []
        dropdowns = self.page.locator("select")

        for index in range(dropdowns.count()):
            dropdown = dropdowns.nth(index)

            if not dropdown.is_visible() or dropdown.is_disabled():
                continue

            option = select_random_available_option(dropdown)

            if option:
                selected.append(option)

        return selected

    def _choose_variation_options(self) -> list[str]:
        selected: list[str] = []

        variation_groups = self.page.locator("[data-testid*='variation' i]")

        for index in range(variation_groups.count()):
            option = pick_random_option_from_container(variation_groups.nth(index))

            if option is None:
                continue

            locator, label = option
            locator.click()

            if label:
                selected.append(f"option:{label}")

        return selected

    def _add_to_cart(self) -> bool:
        button = self.page.get_by_role(
            "button",
            name=re.compile(r"Add to cart", re.IGNORECASE),
        ).first

        expect(button).to_be_visible(timeout=10_000)
        button.click()
        return self._wait_for_cart_page()

    def _wait_for_cart_page(self) -> bool:
        try:
            self.page.wait_for_url(
                re.compile(r"cart|checkout", re.IGNORECASE),
                timeout=10_000,
            )
            return True
        except PlaywrightTimeoutError:
            return False

    def _save_screenshot(self, index: int, success: bool) -> str | None:
        status = "success" if success else "failed"
        path = self.screenshot_dir / f"add-to-cart-item-{index}-{status}.png"

        try:
            self.page.screenshot(path=str(path), full_page=True)
            return str(path)
        except Error as exc:
            logger.warning("Could not save screenshot for item %d: %s", index, exc)
            return None
