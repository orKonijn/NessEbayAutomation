import random
import re
from pathlib import Path

from playwright.sync_api import Error, Page, expect


def log_item_result(
    index: int,
    url: str,
    selected_variants: list[str],
    success: bool,
    error_message: str | None,
    screenshot_path: str,
) -> None:
    print(
        "[add_items_to_cart] "
        f"item={index} url={url} "
        f"selected_variants={selected_variants or 'none'} "
        f"status={'success' if success else 'failed'} "
        f"error={error_message or 'none'} "
        f"screenshot={screenshot_path}"
    )


def is_placeholder_value(value: str) -> bool:
    normalized = value.strip().lower()
    return (
        not normalized
        or normalized in {"select", "choose", "please select"}
        or normalized.startswith("select ")
        or normalized.startswith("choose ")
    )


def select_random_available_option(select_locator) -> str | None:
    options = select_locator.locator("option")
    candidates: list[tuple[str, str]] = []
    for idx in range(options.count()):
        option = options.nth(idx)
        value = (option.get_attribute("value") or "").strip()
        label = (option.inner_text(timeout=1000) or "").strip()
        disabled = option.is_disabled() or (
            option.get_attribute("aria-disabled") == "true"
        )
        if disabled or not value or is_placeholder_value(label):
            continue
        candidates.append((value, label))

    if not candidates:
        return None

    value, label = random.choice(candidates)
    select_locator.select_option(value=value)
    return f"select:{label}"


class ItemPage:
    """eBay item detail page interactions."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self._last_cart_count: int | None = None
        self.screenshot_dir = Path("artifacts/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def add_items_to_cart(self, urls: list[str]) -> None:
        """Open each item URL, select required variants (if present), and add item to cart."""

        for index, url in enumerate(urls, start=1):
            success = self._goto_page(url, index)

            if not success and self.page.is_closed():
                raise RuntimeError(
                    f"Browser page became unusable while processing item {index}: {url}"
                )

    def _goto_page(self, url: str, index: int) -> bool:
        error_message: str | None = None
        selected_variants: list[str] = []
        success = False
        try:
            self.page.goto(url, wait_until="domcontentloaded")
            self._wait_for_item_page_ready()

            selected_variants = self._select_required_variants()
            success = self._click_add_to_cart()

        except Exception as exc:  # continue processing next URL
            error_message = str(exc)
        finally:
            status = "success" if success else "failed"
            screenshot_path = (
                self.screenshot_dir / f"add-to-cart-item-{index}-{status}.png"
            )
            self.page.screenshot(path=str(screenshot_path), full_page=True)
            log_item_result(
                index=index,
                url=url,
                selected_variants=selected_variants,
                success=success,
                error_message=error_message,
                screenshot_path=str(screenshot_path),
            )
        return success

    def _wait_for_item_page_ready(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        ready_targets = [
            self.page.get_by_test_id("x-item-title"),
            self.page.locator("[data-test-id='x-item-title']"),
            self.page.get_by_role("main"),
            self.page.locator("#CenterPanelInternal"),
        ]

        for target in ready_targets:
            if target.count() > 0:
                expect(target.first).to_be_visible(timeout=20_000)
                return

        expect(self.page.locator("body")).to_be_visible(timeout=20_000)

    def _select_required_variants(self) -> list[str]:
        selections: list[str] = []
        selections.extend(self._select_required_dropdown_variants())
        selections.extend(self._select_required_radio_variants())
        selections.extend(self._select_required_button_variants())
        return selections

    def _select_required_dropdown_variants(self) -> list[str]:
        selections: list[str] = []
        dropdowns = self.page.locator(
            "select[required], [data-testid*='select' i] select, [data-test-id*='select' i] select"
        )
        for idx in range(dropdowns.count()):
            select = dropdowns.nth(idx)
            if not select.is_visible() or select.is_disabled():
                continue
            option_value = select_random_available_option(select)
            if option_value:
                selections.append(option_value)
        return selections

    def _select_required_radio_variants(self) -> list[str]:
        selections: list[str] = []
        groups = self.page.locator("fieldset")
        for idx in range(groups.count()):
            group = groups.nth(idx)
            radios = group.get_by_role("radio")
            if radios.count() == 0:
                continue
            available = []
            for r_idx in range(radios.count()):
                radio = radios.nth(r_idx)
                if radio.is_disabled() or not radio.is_visible():
                    continue
                available.append(radio)
            if not available:
                continue
            selected = random.choice(available)
            label = (selected.get_attribute("aria-label") or "").strip()
            selected.check(force=False)
            if label:
                selections.append(f"radio:{label}")
        return selections

    def _select_required_button_variants(self) -> list[str]:
        selections: list[str] = []
        option_containers = self.page.locator(
            "[role='listbox'], [data-testid*='variation' i], [data-test-id*='variation' i]"
        )
        for idx in range(option_containers.count()):
            container = option_containers.nth(idx)
            options = container.get_by_role("option")
            if options.count() == 0:
                options = container.get_by_role("button")
            available = []
            for opt_idx in range(options.count()):
                option = options.nth(opt_idx)
                if option.is_disabled() or not option.is_visible():
                    continue
                name = (option.inner_text(timeout=1000) or "").strip()
                if is_placeholder_value(name):
                    continue
                available.append((option, name))
            if not available:
                continue
            chosen, name = random.choice(available)
            chosen.click()
            selections.append(f"option:{name}")
        return selections

    def _click_add_to_cart(self) -> bool:
        previous_count = self._read_cart_count()

        add_to_cart_btn = self.page.get_by_role(
            "button", name=re.compile(r"Add to (cart|basket)", re.IGNORECASE)
        )
        if add_to_cart_btn.count() == 0:
            add_to_cart_btn = self.page.locator(
                "[data-testid*='add-to-cart' i], [data-test-id*='add-to-cart' i], #atcBtn_btn_1"
            )

        expect(add_to_cart_btn.first).to_be_visible(timeout=10_000)
        add_to_cart_btn.first.click()

        success_signal = self._wait_for_add_to_cart_success(previous_count)
        self._last_cart_count = self._read_cart_count()
        return success_signal

    def _wait_for_add_to_cart_success(self, previous_count: int | None) -> bool:
        try:
            self.page.wait_for_url(
                re.compile(r"cart|checkout|viCart", re.IGNORECASE), timeout=10_000
            )
            return True
        except Error:
            pass

        success_locators = [
            self.page.get_by_text(
                re.compile(r"added to (your )?(cart|basket)", re.IGNORECASE)
            ),
            self.page.locator("[role='dialog']"),
            self.page.locator("[aria-live='polite']"),
        ]
        for locator in success_locators:
            if locator.count() > 0:
                try:
                    expect(locator.first).to_be_visible(timeout=8_000)
                    return True
                except Error:
                    continue

        if previous_count is not None:
            try:
                expect.poll(
                    lambda: self._read_cart_count() or 0, timeout=8_000
                ).to_be_greater_than(previous_count)
                return True
            except Error:
                return False
        return False

    def _read_cart_count(self) -> int | None:
        cart_badge = self.page.locator("#gh-cart-n, [data-testid='cart-badge']").first
        if cart_badge.count() == 0 or not cart_badge.is_visible():
            return None
        text = (cart_badge.inner_text() or "").strip()
        digits = "".join(ch for ch in text if ch.isdigit())
        return int(digits) if digits else 0
