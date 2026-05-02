import re
from pathlib import Path

from playwright.sync_api import Error, Locator, Page, expect

from ebay.utils.price_parser import parse_price


class CartPage:
    """eBay cart page interactions and assertions."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.screenshot_dir = Path("artifacts/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def assert_cart_total_not_exceeds(
        self,
        budget_per_item: float,
        items_count: int,
    ) -> None:
        self._open_cart()
        self.save_cart_screenshot()

        cart_total = self.get_cart_total()
        max_allowed_total = budget_per_item * items_count

        assert cart_total <= max_allowed_total, (
            "Cart total exceeds allowed maximum. "
            f"Actual cart total: {cart_total:.2f}; "
            f"Expected max total: {max_allowed_total:.2f}; "
            f"Budget per item: {budget_per_item:.2f}; "
            f"Item count: {items_count}."
        )

    def _open_cart(self) -> None:
        try:
            if re.search(r"cart|viCart", self.page.url, re.IGNORECASE):
                self.page.wait_for_load_state("domcontentloaded")
            else:
                self.page.goto("https://cart.ebay.com/", wait_until="domcontentloaded")

            if not re.search(r"cart|viCart", self.page.url, re.IGNORECASE):
                cart_button = self.page.get_by_role(
                    "link", name=re.compile(r"cart", re.IGNORECASE)
                )
                if cart_button.count() > 0:
                    cart_button.first.click()
                    self.page.wait_for_load_state("domcontentloaded")

            expect(self.page).to_have_url(re.compile(r"cart|viCart", re.IGNORECASE))
            expect(self.page.locator("body")).to_be_visible(timeout=15_000)
        except Error as exc:
            raise RuntimeError(f"Failed to load eBay cart page: {exc}") from exc

    def get_cart_total(self) -> float:
        preferred_patterns = [
            r"item\s*subtotal",
            r"subtotal",
            r"order\s*total",
            r"total",
        ]

        for pattern in preferred_patterns:
            labeled_value = self._value_near_label(pattern)
            if labeled_value is not None:
                return labeled_value

        text_patterns = [
            r"item\s*subtotal[^\d$]*([\w\s$,.]+)",
            r"subtotal[^\d$]*([\w\s$,.]+)",
            r"order\s*total[^\d$]*([\w\s$,.]+)",
            r"total[^\d$]*([\w\s$,.]+)",
        ]

        body_text = self.page.locator("body").inner_text()
        for pattern in text_patterns:
            match = re.search(pattern, body_text, flags=re.IGNORECASE)
            if not match:
                continue

            parsed = parse_price(match.group(0))
            if parsed is not None:
                return parsed

        raise RuntimeError(
            "Could not find cart subtotal/total on the cart page. "
            "Looked for labels: Subtotal, Item subtotal, Total, Order total."
        )

    def _value_near_label(self, label_pattern: str) -> float | None:
        containers = self.page.locator(
            "[data-testid], [data-test-id], [role='row'], [role='listitem'], "
            "[aria-label], section, div, li"
        )

        max_checks = min(containers.count(), 150)
        for idx in range(max_checks):
            container = containers.nth(idx)
            if not container.is_visible():
                continue

            try:
                text = container.inner_text(timeout=500)
            except Error:
                continue

            if not re.search(label_pattern, text, flags=re.IGNORECASE):
                continue

            parsed = parse_price(text)
            if parsed is not None:
                return parsed

        return None

    def save_cart_screenshot(
        self, path: str = "artifacts/screenshots/cart-total-check.png"
    ) -> None:
        screenshot_path = Path(path)
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=str(screenshot_path), full_page=True)
