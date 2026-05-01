import os
from pathlib import Path
from typing import Any, Generator

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Browser, BrowserType, Page, Playwright, sync_playwright

from ebay.pages.home_page import HomePage
from tests.config.playwright_config import PlaywrightConfig

REPO_ROOT = Path(__file__).resolve().parents[1]
AUTH_STATE_PATH = REPO_ROOT / ".auth" / "ebay-auth.json"

load_dotenv(REPO_ROOT / ".env")


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
    playwright: Playwright,
    app_config: PlaywrightConfig,
) -> Generator[Browser, Any, None]:
    browser_type: BrowserType = getattr(playwright, app_config.browser_name)
    browser = browser_type.launch(headless=app_config.headless)

    yield browser

    browser.close()


@pytest.fixture(scope="session", autouse=True)
def before_all_login(browser: Browser, base_url: str) -> None:
    print("Running before all login")

    mail = os.getenv("EBAY_EMAIL")
    password = os.getenv("EBAY_PASSWORD")

    if not mail:
        raise ValueError("EBAY_EMAIL is missing from .env")
    if not password:
        raise ValueError("EBAY_PASSWORD is missing from .env")

    AUTH_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)

    context = browser.new_context(base_url=base_url)
    page = context.new_page()

    home = HomePage(page).open()
    home.login_page.login(mail, password)

    context.storage_state(path=str(AUTH_STATE_PATH))
    context.close()


@pytest.fixture()
def page(
    browser: Browser,
    base_url: str,
    before_all_login: None,
) -> Generator[Page, Any, None]:
    context = browser.new_context(
        base_url=base_url,
        storage_state=str(AUTH_STATE_PATH),
    )

    page = context.new_page()

    yield page

    context.close()
