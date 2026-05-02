import logging
import re
from pathlib import Path

from playwright.sync_api import Error, Page, expect

from ebay.utils.allure_attachments import save_page_screenshot
from ebay.utils.price_parser import parse_price

logger = logging.getLogger(__name__)


class CartPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.screenshot_dir = Path("artifacts/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def assert_cart_total_not_exceeds(
        self, budget_per_item: float, items_count: int
    ) -> None:
        self._open_cart()

        screenshot_path = self.save_cart_screenshot()

        cart_total = self.get_cart_total()
        max_allowed_total = budget_per_item * items_count

        logger.info(
            "Cart total check | actual=%.2f | max_allowed=%.2f | "
            "budget_per_item=%.2f | items_count=%d | screenshot=%s",
            cart_total,
            max_allowed_total,
            budget_per_item,
            items_count,
            screenshot_path,
        )

        assert cart_total <= max_allowed_total, (
            "Cart total exceeds allowed maximum. "
            f"Actual: {cart_total:.2f}; Max allowed: {max_allowed_total:.2f}; "
            f"Budget/item: {budget_per_item:.2f}; Item count: {items_count}."
        )

    def _open_cart(self) -> None:
        try:
            if not re.search(r"cart|viCart", self.page.url, re.IGNORECASE):
                self.page.goto("https://cart.ebay.com/", wait_until="domcontentloaded")

            if not re.search(r"cart|viCart", self.page.url, re.IGNORECASE):
                cart_link = self.page.get_by_role(
                    "link", name=re.compile(r"cart", re.IGNORECASE)
                )
                expect(cart_link.first).to_be_visible(timeout=10_000)
                cart_link.first.click()

            expect(self.page).to_have_url(re.compile(r"cart|viCart", re.IGNORECASE))
            expect(self.page.locator("body")).to_be_visible(timeout=15_000)

        except Error as exc:
            raise RuntimeError(f"Failed to load cart page: {exc}") from exc

    def get_cart_total(self) -> float:
        subtotal_locators = (
            self.page.locator("[data-test-id='SUBTOTAL']").first,
            self.page.locator(
                ".cart-summary-line-item [data-test-id='SUBTOTAL']"
            ).first,
            self.page.locator(".val-col.total-row[data-test-id='SUBTOTAL']").first,
        )

        for locator in subtotal_locators:
            if locator.count() == 0 or not locator.is_visible():
                continue

            subtotal_text = locator.inner_text(timeout=1_000)
            logger.info("Found cart subtotal text: %s", subtotal_text)

            parsed = parse_price(subtotal_text)
            if parsed is not None:
                return parsed

        raise RuntimeError(
            "Could not find a parseable cart subtotal value on the cart page."
        )

    def save_cart_screenshot(
        self, path: str = "artifacts/screenshots/cart-total-check.png"
    ) -> Path:
        screenshot_path = Path(path)
        save_page_screenshot(
            self.page,
            screenshot_path,
            name="Cart total check",
        )
        return screenshot_path
