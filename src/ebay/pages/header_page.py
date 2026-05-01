from playwright.sync_api import Page, expect

from ebay.pages.login_page import LoginPage


class HeaderPage(LoginPage):

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.page = page
