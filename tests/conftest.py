import os
from typing import Any, Generator

import pytest
from playwright.sync_api import Browser, Page, Playwright, sync_playwright


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("BASE_URL", "https://www.ebay.com")


@pytest.fixture(scope="session")
def playwright() -> Generator[Playwright, Any, None]:
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright: Playwright) -> Generator[Browser, Any, None]:
    browser = playwright.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture()
def page(browser: Browser, base_url: str) -> Generator[Page, Any, None]:
    context = browser.new_context(base_url=base_url)
    page = context.new_page()
    yield page
    context.close()