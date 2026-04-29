import re

import allure
from playwright.sync_api import Page, expect

from ebay.pages.base_page import BasePage


class SearchResultsPage(BasePage):
    """eBay search results page interactions and assertions."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.result_titles = page.locator("li.s-item .s-item__title").filter(
            has_text=re.compile(r"\S"),
        )

    @allure.step("Verify search results loaded for: {term}")
    def assert_loaded_for(self, term: str) -> "SearchResultsPage":
        encoded_main_word = re.escape(term.split()[0])
        expect(self.page).to_have_url(re.compile(r".*_nkw=.*", re.IGNORECASE), timeout=15_000)
        expect(self.page.locator("body")).to_contain_text(
            re.compile(encoded_main_word, re.IGNORECASE),
            timeout=15_000,
        )
        return self

    @allure.step("Verify visible product results exist")
    def assert_has_visible_results(self) -> "SearchResultsPage":
        expect(self.result_titles.first).to_be_visible(timeout=15_000)
        return self

    @allure.step("Read first visible result title")
    def first_result_title(self) -> str:
        expect(self.result_titles.first).to_be_visible(timeout=15_000)
        return self.result_titles.first.inner_text().strip()
