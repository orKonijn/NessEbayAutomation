import re

import allure
from playwright.sync_api import Locator, Page, expect

from ebay.utils.extract import extract_item_price, extract_item_url


class AdvancedSearch:
    def __init__(self, page: Page) -> None:
        self.page = page

    @allure.step("Search eBay by query and return result URLs under max price")
    def search_items_by_query(
        self, query: str, max_price: float, limit: int = 5
    ) -> list[str]:
        if limit <= 0:
            return []

        self._navigate_to_advanced_search()
        self._fill_search_form(query=query, max_price=max_price)
        self._submit_search()
        return self._collect_matching_item_urls(max_price=max_price, limit=limit)

    def _navigate_to_advanced_search(self) -> None:
        self.page.get_by_role(
            "link", name=re.compile("Advanced", re.IGNORECASE)
        ).first.click()
        expect(self.page).to_have_title(re.compile("Advanced", re.IGNORECASE))

    def _fill_search_form(self, query: str, max_price: float) -> None:
        self.page.get_by_role(
            "textbox", name=re.compile(r"Enter keywords|keywords", re.IGNORECASE)
        ).first.fill(query)

        max_price_input = self.page.get_by_label(
            re.compile(r"Maximum Price|max", re.IGNORECASE)
        )
        if max_price_input.count() == 0:
            max_price_input = self.page.locator("input[name='_udhi'], #_udhi")
        max_price_input.first.fill(str(max_price))

    def _submit_search(self) -> None:
        self.page.get_by_role(
            "button", name=re.compile(r"Search", re.IGNORECASE)
        ).first.click()
        expect(self.page).to_have_url(re.compile(r"ebay\.com/sch/", re.IGNORECASE))

    def _collect_matching_item_urls(self, max_price: float, limit: int) -> list[str]:
        matches: list[str] = []
        visited_urls: set[str] = set()

        for _ in range(2):
            visited_urls.add(self.page.url)
            self._collect_matches_from_page(
                matches=matches, max_price=max_price, limit=limit
            )
            if len(matches) >= limit or not self._go_to_next_results_page(visited_urls):
                break
        return matches

    def _collect_matches_from_page(
        self, matches: list[str], max_price: float, limit: int
    ) -> None:
        result_items = self.page.locator("li.s-item")
        for index in range(result_items.count()):
            item_card = result_items.nth(index)
            item_url = extract_item_url(item_card)
            if not item_url or item_url in matches:
                continue

            item_price = extract_item_price(item_card)
            if item_price is None or item_price > max_price:
                continue

            matches.append(item_url)
            if len(matches) >= limit:
                return

    def _go_to_next_results_page(self, visited_urls: set[str]) -> bool:
        next_link: Locator = self.page.get_by_role(
            "link", name=re.compile(r"^Next$", re.IGNORECASE)
        ).first
        if next_link.count() == 0 or not next_link.is_visible():
            return False

        if (next_link.get_attribute("aria-disabled") or "").lower() == "true":
            return False

        previous_url = self.page.url
        next_link.click()
        self.page.wait_for_url(re.compile(r"(_pgn=|sch/i\.html)", re.IGNORECASE))
        return self.page.url not in {previous_url, *visited_urls}
