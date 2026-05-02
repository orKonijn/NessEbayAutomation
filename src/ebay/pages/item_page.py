import logging
import random
import re
from pathlib import Path

import allure
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

logger = logging.getLogger(__name__)


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


class ItemPage:
    """eBay item detail page interactions."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.screenshot_dir = Path("artifacts/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    @allure.step("Add items to cart")
    def add_items_to_cart(self, urls: list[str]) -> None:
        logger.info("Starting add-to-cart flow | items_count=%d", len(urls))

        allure.attach(
            "\n".join(urls),
            name="Item URLs",
            attachment_type=allure.attachment_type.TEXT,
        )

        for index, url in enumerate(urls, start=1):
            self._process_item(index=index, url=url)

        logger.info("Finished add-to-cart flow | items_count=%d", len(urls))

    @allure.step("Process item #{index}")
    def _process_item(self, index: int, url: str) -> None:
        selected_variants: list[str] = []
        success = False
        error_message: str | None = None

        logger.info("Processing item | index=%d | url=%s", index, url)

        allure.dynamic.parameter("item_index", index)
        allure.dynamic.parameter("item_url", url)

        try:
            with allure.step("Open item page"):
                self.page.goto(url, wait_until="domcontentloaded", timeout=30_000)

                logger.info(
                    "Item page loaded | index=%d | current_url=%s",
                    index,
                    self.page.url,
                )

            with allure.step("Wait for item page content"):
                self._wait_for_item_page()

            with allure.step("Select item variants"):
                selected_variants = self._select_variants()

                allure.attach(
                    (
                        "\n".join(selected_variants)
                        if selected_variants
                        else "No variants selected"
                    ),
                    name=f"Selected variants - item {index}",
                    attachment_type=allure.attachment_type.TEXT,
                )

                logger.info(
                    "Selected variants | index=%d | variants=%s",
                    index,
                    selected_variants,
                )

            with allure.step("Click Add to cart"):
                success = self._click_add_to_cart()

                logger.info(
                    "Add-to-cart completed | index=%d | success=%s",
                    index,
                    success,
                )

        except Exception as exc:
            error_message = str(exc)

            allure.attach(
                error_message,
                name=f"Error message - item {index}",
                attachment_type=allure.attachment_type.TEXT,
            )

            logger.exception(
                "Failed to process item | index=%d | url=%s",
                index,
                url,
            )

        finally:
            screenshot_path = self._save_screenshot(index=index, success=success)

            if screenshot_path:
                allure.attach.file(
                    screenshot_path,
                    name=f"Item {index} screenshot - "
                    f"{'success' if success else 'failed'}",
                    attachment_type=allure.attachment_type.PNG,
                )

            allure.attach(
                (
                    f"Index: {index}\n"
                    f"URL: {url}\n"
                    f"Success: {success}\n"
                    f"Selected variants: {selected_variants}\n"
                    f"Error: {error_message or 'None'}\n"
                    f"Screenshot: {screenshot_path or 'N/A'}"
                ),
                name=f"Item {index} result summary",
                attachment_type=allure.attachment_type.TEXT,
            )

            log_item_result(
                index=index,
                url=url,
                selected_variants=selected_variants,
                success=success,
                error_message=error_message,
                screenshot_path=screenshot_path or None,
            )

            logger.info(
                "Item result logged | index=%d | success=%s | screenshot=%s",
                index,
                success,
                screenshot_path or "N/A",
            )

    @allure.step("Wait for item page content")
    def _wait_for_item_page(self) -> None:
        logger.debug("Waiting for item page main content.")

        item_content = self.page.locator(
            "[data-testid='x-item-title'], "
            "[data-test-id='x-item-title'], "
            "#CenterPanelInternal, "
            "main"
        ).first

        expect(item_content).to_be_visible(timeout=20_000)

        logger.info("Item page main content is visible.")

    @allure.step("Select item variants")
    def _select_variants(self) -> list[str]:
        logger.debug("Selecting item variants.")

        selections: list[str] = []

        selections.extend(self._select_dropdown_variants())
        selections.extend(self._select_clickable_variants())

        logger.info("Variant selection completed | selections=%s", selections)

        return selections

    @allure.step("Select dropdown variants")
    def _select_dropdown_variants(self) -> list[str]:
        selections: list[str] = []

        dropdowns = self.page.locator("select")
        dropdowns_count = dropdowns.count()

        logger.debug("Found dropdown variants | count=%d", dropdowns_count)

        for index in range(dropdowns_count):
            dropdown = dropdowns.nth(index)

            if not dropdown.is_visible() or dropdown.is_disabled():
                logger.debug("Skipping unavailable dropdown | index=%d", index)
                continue

            selected = select_random_available_option(dropdown)

            if selected:
                selections.append(selected)

        logger.info("Dropdown variant selections | selections=%s", selections)

        return selections

    @allure.step("Select clickable variants")
    def _select_clickable_variants(self) -> list[str]:
        selections: list[str] = []

        variant_containers = self.page.locator(
            "fieldset, "
            "[role='listbox'], "
            "[data-testid*='variation' i], "
            "[data-test-id*='variation' i]"
        )

        containers_count = variant_containers.count()

        logger.debug(
            "Found clickable variant containers | count=%d",
            containers_count,
        )

        for index in range(containers_count):
            container = variant_containers.nth(index)

            option = pick_random_option_from_container(container)

            if option is None:
                logger.debug("No clickable option found | container_index=%d", index)
                continue

            locator, label = option
            locator.click()

            logger.info(
                "Selected clickable variant | container_index=%d | label=%s",
                index,
                label,
            )

            if label:
                selections.append(f"option:{label}")

        logger.info("Clickable variant selections | selections=%s", selections)

        return selections

    @allure.step("Click Add to cart button")
    def _click_add_to_cart(self) -> bool:
        logger.debug("Looking for Add to cart button.")

        button = self.page.get_by_role(
            "button",
            name=re.compile(r"Add to (cart|basket)", re.IGNORECASE),
        )

        if button.count() == 0:
            logger.debug(
                "Role-based Add to cart button not found. Using fallback selectors."
            )

            button = self.page.locator(
                "[data-testid*='add-to-cart' i], "
                "[data-test-id*='add-to-cart' i], "
                "#atcBtn_btn_1"
            )

        expect(button.first).to_be_visible(timeout=10_000)

        logger.info("Clicking Add to cart button.")

        button.first.click()

        success = self._wait_for_cart_confirmation()

        logger.info("Cart confirmation result | success=%s", success)

        return success

    @allure.step("Wait for cart confirmation")
    def _wait_for_cart_confirmation(self) -> bool:
        logger.debug("Waiting for cart confirmation.")

        try:
            self.page.wait_for_url(
                re.compile(r"cart|checkout|viCart", re.IGNORECASE),
                timeout=10_000,
            )

            logger.info(
                "Cart confirmation detected by URL | current_url=%s",
                self.page.url,
            )

            return True

        except PlaywrightTimeoutError:
            logger.debug(
                "Cart confirmation URL was not detected. Checking page content."
            )

        confirmation_candidates = (
            self.page.get_by_text(
                re.compile(r"added to (your )?(cart|basket)", re.IGNORECASE)
            ),
            self.page.locator("[role='dialog']"),
            self.page.locator("[aria-live='polite']"),
        )

        for confirmation in confirmation_candidates:
            try:
                expect(confirmation.first).to_be_visible(timeout=8_000)

                logger.info(
                    "Cart confirmation detected by visible confirmation element."
                )

                return True

            except Error:
                continue

        logger.warning("Cart confirmation was not detected.")

        return False

    @allure.step("Save item screenshot")
    def _save_screenshot(self, index: int, success: bool) -> str:
        status = "success" if success else "failed"
        screenshot_path = self.screenshot_dir / f"add-to-cart-item-{index}-{status}.png"

        try:
            self.page.screenshot(path=str(screenshot_path), full_page=True)

            logger.info(
                "Saved item screenshot | index=%d | success=%s | path=%s",
                index,
                success,
                screenshot_path,
            )

            return str(screenshot_path)

        except Error:
            logger.exception(
                "Failed to save item screenshot | index=%d | success=%s | path=%s",
                index,
                success,
                screenshot_path,
            )

            return ""
