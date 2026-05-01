import re
from typing import Optional

import allure
from playwright.sync_api import Page, expect

from ebay.pages.header_page import HeaderPage


def extract_item_url(result_item) -> Optional[str]:
    item_link = result_item.locator(
        "xpath=.//a[contains(@class,'s-item__link') and starts-with(@href,'http')]"
    ).first
    href = item_link.get_attribute("href")
    if not href or "ebay.com/itm/" not in href:
        return None
    return href


class AdvancedSearch:

    def __init__(self, page: Page) -> None:
        self.page: Page = page
        self.header = HeaderPage(page)

    @allure.step("Search eBay by name and return URLs under max price")
    def search_items_by_query(
        self, query: str, max_price: float, limit: int = 5
    ) -> list[str]:
        if limit <= 0:
            return []

        self._open_advanced_search_and_submit(query=query, max_price=max_price)
        return self._collect_matching_item_urls(max_price=max_price, limit=limit)

    def _open_advanced_search_and_submit(self, query: str, max_price: float) -> None:
        self._navigate_to_advanced_search()
        self._fill_advanced_search_form(query=query, max_price=max_price)
        self._submit_search()

    def _collect_matching_item_urls(self, max_price: float, limit: int) -> list[str]:
        matches: list[str] = []
        visited_urls: set[str] = set()
        max_pages = 2

        for _ in range(max_pages):
            visited_urls.add(self.page.url)
            self._collect_matches_from_current_page(
                matches=matches,
                max_price=max_price,
                limit=limit,
            )
            if len(matches) >= limit or not self._go_to_next_results_page(visited_urls):
                break
        print(matches)
        return matches

    def _navigate_to_advanced_search(self) -> None:
        self.page.get_by_role(
            "link", name=re.compile(r"Advanced", re.IGNORECASE)
        ).first.click()
        self.page.wait_for_load_state("domcontentloaded")
        expect(self.page).to_have_title(re.compile(r"Advanced", re.IGNORECASE))

    def _fill_advanced_search_form(self, query: str, max_price: float) -> None:
        self.page.pause()
        query_input = self.page.get_by_role(
            "textbox", name=re.compile(r"Enter keywords", re.IGNORECASE)
        )
        if query_input.count() == 0:
            query_input = self.page.locator("[aria-label*='keywords' i], #_nkw")
        query_input.first.fill(query)

        max_price_input = self.page.locator(
            "[data-testid='s0-1-17-5-1[2]-0-1[2]-1-2[2]-10-textrange-textbox'], input[name='_udhi'], #_udhi"
        ).first
        if max_price_input.count() > 0 and max_price_input.is_visible():
            max_price_input.fill(str(max_price))

    def _submit_search(self) -> None:
        search_button = self.page.get_by_role(
            "button", name=re.compile(r"Search", re.IGNORECASE)
        ).first
        if search_button.count() == 0:
            search_button = self.page.locator(
                "#searchBtnLowerLnk, #searchBtnUpperLnk"
            ).first
        search_button.click()
        self.page.wait_for_load_state("domcontentloaded")
        expect(self.page).to_have_url(re.compile(r"ebay\.com/sch/", re.IGNORECASE))

    def _collect_matches_from_current_page(
        self, matches: list[str], max_price: float, limit: int
    ) -> None:
        result_items = self.page.locator("xpath=//li[contains(@class,'s-item')]")
        count = result_items.count()

        for idx in range(count):
            card = result_items.nth(idx)
            item_url = extract_item_url(card)
            if not item_url or item_url in matches:
                continue

            item_price = extract_item_url(card)
            if item_price is None or item_price > str(max_price):
                continue

            matches.append(item_url)
            if len(matches) >= limit:
                return

    def _go_to_next_results_page(self, visited_urls: set[str]) -> bool:
        next_link = self.page.get_by_role(
            "link", name=re.compile(r"^Next$", re.IGNORECASE)
        ).first
        if next_link.count() == 0 or not next_link.is_visible():
            return False

        aria_disabled = next_link.get_attribute("aria-disabled")
        if aria_disabled and aria_disabled.lower() == "true":
            return False

        current_url = self.page.url
        next_link.click()
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_url(re.compile(r".*_pgn=.*|.*sch/i\.html.*"), timeout=15_000)
        if self.page.url == current_url or self.page.url in visited_urls:
            return False

        return True
