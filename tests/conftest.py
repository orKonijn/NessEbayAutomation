import os
from typing import Any, Generator

import pytest
from playwright.sync_api import Browser, BrowserType, Page, Playwright, sync_playwright

from playwright_config import PlaywrightConfig


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run browser in headed mode (overrides HEADLESS env variable).",
    )


@pytest.fixture(scope="session")
def config(config: pytest.Config) -> PlaywrightConfig:
    settings = PlaywrightConfig.from_env()
    if config.getoption("headed"):
        return PlaywrightConfig(
            base_url=settings.base_url,
            browser_name=settings.browser_name,
            headless=False,
        )
    return settings


@pytest.fixture(scope="session")
def base_url(config: PlaywrightConfig) -> str:
    return config.base_url


@pytest.fixture(scope="session")
def playwright() -> Generator[Playwright, Any, None]:
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright: Playwright, config: PlaywrightConfig) -> Generator[Browser, Any, None]:
    browser_type: BrowserType = getattr(playwright, config.browser_name)
    browser = browser_type.launch(headless=config.headless)
    yield browser
    browser.close()


@pytest.fixture()
def page(browser: Browser, base_url: str) -> Generator[Page, Any, None]:
    context = browser.new_context(base_url=base_url)
    page = context.new_page()
    yield page
    context.close()