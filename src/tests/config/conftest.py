from pathlib import Path
from typing import Any, Generator

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Browser, BrowserType, Page, Playwright, sync_playwright

from playwright_config import PlaywrightConfig

ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")


@pytest.fixture(scope="session")
def app_config(pytestconfig: pytest.Config) -> PlaywrightConfig:
    settings = PlaywrightConfig.from_env()

    if pytestconfig.getoption("headed"):
        return PlaywrightConfig(
            base_url=settings.base_url,
            browser_name=settings.browser_name,
            headless=False,
        )

    return settings


@pytest.fixture(scope="session")
def base_url(app_config: PlaywrightConfig) -> str:
    return app_config.base_url


@pytest.fixture(scope="session")
def playwright() -> Generator[Playwright, Any, None]:
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(
    playwright: Playwright, app_config: PlaywrightConfig
) -> Generator[Browser, Any, None]:
    browser_type: BrowserType = getattr(playwright, app_config.browser_name)
    browser = browser_type.launch(headless=app_config.headless)

    yield browser

    browser.close()


@pytest.fixture()
def page(browser: Browser, base_url: str) -> Generator[Page, Any, None]:
    context = browser.new_context(base_url=base_url)
    page = context.new_page()

    yield page

    context.close()
