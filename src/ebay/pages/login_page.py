import logging
import os
import re
from pathlib import Path

import allure
from dotenv import load_dotenv
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


def mask_email(email: str) -> str:
    if "@" not in email:
        return "***"
    username, domain = email.split("@", maxsplit=1)
    visible = username[:2] if len(username) > 2 else username[:1]
    return f"{visible}***@{domain}"


class LoginPage:
    def __init__(self, page: Page) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        load_dotenv(repo_root / ".env")
        self.page = page
        self.screenshot_dir = Path("artifacts/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    @allure.step("Login with eBay account")
    def login(self, email: str | None = None, password: str | None = None) -> None:
        email, password = self._resolve_credentials(email, password)
        masked_email = mask_email(email)

        allure.dynamic.parameter("email", masked_email)
        logger.info("Logging in as %s", masked_email)

        try:
            self.page.get_by_role(
                "link", name=re.compile(r"^Sign in$", re.IGNORECASE)
            ).click()
            self.page.get_by_test_id("userid").fill(email)
            self.page.get_by_test_id("signin-continue-btn").click()
            self.page.get_by_test_id("pass").fill(password)
            self.page.get_by_test_id("sgnBt").click()
        except Exception:
            screenshot_path = self.screenshot_dir / "login-failure.png"
            self.page.screenshot(path=str(screenshot_path), full_page=True)
            allure.attach.file(
                str(screenshot_path),
                name="Login failure screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
            raise

        expect(
            self.page.get_by_role("link", name=re.compile(r"^Sign in$", re.IGNORECASE))
        ).not_to_be_visible(timeout=15_000)

    def _resolve_credentials(
        self,
        email: str | None,
        password: str | None,
    ) -> tuple[str, str]:
        resolved_email = email or os.getenv("EBAY_EMAIL")
        resolved_password = password or os.getenv("EBAY_PASSWORD")

        if not resolved_email:
            raise ValueError("EBAY_EMAIL is missing. Add it to your .env file.")
        if not resolved_password:
            raise ValueError("EBAY_PASSWORD is missing. Add it to your .env file.")

        expect(self.page.locator("body")).to_be_visible(timeout=10_000)
        return resolved_email, resolved_password
