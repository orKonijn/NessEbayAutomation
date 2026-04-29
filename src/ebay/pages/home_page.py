import re

import allure
from playwright.sync_api import Page, expect

from ebay.pages.base_page import BasePage
from ebay.pages.search_results_page import SearchResultsPage


class HomePage(BasePage):
    """eBay home page interactions."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.search_input = page.get_by_role(
            "textbox",
            name=re.compile("search for anything", re.IGNORECASE),
        )

    @allure.step("Open eBay home page")
    def open(self) -> "HomePage":
        self.page.goto("/", wait_until="domcontentloaded")
        expect(self.page).to_have_title(re.compile("eBay", re.IGNORECASE), timeout=15_000)
        return self

    @allure.step("Verify search is ready")
    def assert_search_is_ready(self) -> "HomePage":
        expect(self.search_input).to_be_visible(timeout=15_000)
        expect(self.search_input).to_be_enabled()
        return self

    @allure.step("Search for product: {term}")
    def search_for(self, term: str) -> SearchResultsPage:
        self.assert_search_is_ready()
        self.search_input.fill(term)
        self.search_input.press("Enter")
        return SearchResultsPage(self.page)
