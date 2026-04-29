from playwright.sync_api import Page, expect


class BasePage:
    """Common behavior shared by all page objects."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def assert_page_has_loaded(self) -> None:
        expect(self.page.locator("body")).to_be_visible(timeout=15_000)
