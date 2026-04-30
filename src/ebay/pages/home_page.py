import re

import allure
from playwright.sync_api import Page, expect

from ebay.pages.base_page import BasePage
from ebay.pages.search_results_page import SearchResultsPage
from ebay.pages.header_page import HeaderPage


class HomePage(BasePage, HeaderPage):
    """eBay home page interactions."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @allure.step("Open eBay home page")
    def open(self) -> "HomePage":
        self.page.goto("https://www.ebay.com/", wait_until="domcontentloaded")
        expect(self.page).to_have_url("https://www.ebay.com/")
        expect(self.page).to_have_title(re.compile("eBay", re.IGNORECASE))
        return self
