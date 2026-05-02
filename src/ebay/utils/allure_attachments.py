import logging
from pathlib import Path

import allure
from playwright.sync_api import Error, Page

logger = logging.getLogger(__name__)


def attach_screenshot_file(path: str | Path, name: str) -> None:
    screenshot_path = Path(path)
    if not screenshot_path.exists():
        logger.warning("Screenshot file does not exist: %s", screenshot_path)
        return

    allure.attach.file(
        str(screenshot_path),
        name=name,
        attachment_type=allure.attachment_type.PNG,
    )


def save_page_screenshot(page: Page, path: str | Path, name: str) -> str | None:
    screenshot_path = Path(path)
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        page.screenshot(path=str(screenshot_path), full_page=True)
    except Error as exc:
        logger.warning("Could not save screenshot %s: %s", screenshot_path, exc)
        return None

    attach_screenshot_file(screenshot_path, name=name)
    logger.info("Saved screenshot: %s", screenshot_path)
    return str(screenshot_path)
