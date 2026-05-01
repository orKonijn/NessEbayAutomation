from playwright.sync_api import Page

from ebay.pages.base_page import BasePage
from ebay.pages.header_page import HeaderPage


class HomePage(BasePage, HeaderPage):
    """eBay home page interactions."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
