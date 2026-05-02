import re

import allure
from playwright.sync_api import Page, expect

from ebay.pages.advanced_search import AdvancedSearch
from ebay.pages.base_page import BasePage
from ebay.pages.header_page import HeaderPage
from ebay.pages.item_page import ItemPage
from ebay.pages.cart_page import CartPage


class EbaySite(BasePage):
    """eBay home page interactions."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header = HeaderPage(page)
        self.advanced_search = AdvancedSearch(page)
        self.item_page = ItemPage(page)
        self.cart_page = CartPage(page)

    @allure.step("Open eBay home page")
    def open(self, url: str = "https://www.ebay.com/") -> "HomePage":
        self.page.goto(url, wait_until="domcontentloaded")
        expect(self.page).to_have_url(url)
        expect(self.page).to_have_title(re.compile("eBay", re.IGNORECASE))
        return self
