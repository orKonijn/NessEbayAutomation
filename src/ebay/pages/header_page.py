from playwright.sync_api import Page

from ebay.pages.login_page import LoginPage


class HeaderPage:

    def __init__(self, page: Page) -> None:
        self.page = page
        self.login_page = LoginPage(self.page)
