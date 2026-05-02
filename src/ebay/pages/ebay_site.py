import logging
import re

import allure
from playwright.sync_api import Page, expect

from ebay.pages.advanced_search import AdvancedSearch
from ebay.pages.base_page import BasePage
from ebay.pages.cart_page import CartPage
from ebay.pages.header_page import HeaderPage
from ebay.pages.item_page import ItemPage

logger = logging.getLogger(__name__)


class EbaySite(BasePage):
    """Top-level page object wiring for eBay flows."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header = HeaderPage(page)
        self.advanced_search = AdvancedSearch(page)
        self.item_page = ItemPage(page)
        self.cart_page = CartPage(page)

    @allure.step("Open eBay home page")
    def open(self, url: str = "https://www.ebay.com/") -> "EbaySite":
        logger.info("Opening eBay home page | url=%s", url)

        self.page.goto(url, wait_until="domcontentloaded")

        expect(self.page).to_have_url(re.compile(r"ebay\.com", re.IGNORECASE))
        expect(self.page).to_have_title(re.compile(r"eBay", re.IGNORECASE))

        logger.info(
            "eBay home page opened successfully | current_url=%s | title=%s",
            self.page.url,
            self.page.title(),
        )

        return self
