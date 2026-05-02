import re
from pathlib import Path

import pytest

from ebay.utils.allure_attachments import save_page_screenshot

SCREENSHOT_DIR = Path("artifacts/screenshots")


def _safe_screenshot_name(nodeid: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", nodeid).strip("-")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    page = item.funcargs.get("page")
    if page is None or page.is_closed():
        return

    save_page_screenshot(
        page,
        SCREENSHOT_DIR / f"{_safe_screenshot_name(item.nodeid)}-failed.png",
        name=f"{item.name} failure screenshot",
    )
