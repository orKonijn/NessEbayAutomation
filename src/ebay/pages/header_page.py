import re
import os
from pathlib import Path

import allure
from dotenv import load_dotenv
from playwright.sync_api import Page, expect


class HeaderPage:

    def __init__(self, page: Page) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        load_dotenv(repo_root / ".env")
        self.page = page

    @allure.step("Login with email")
    def login(self, email: str | None = None) -> None:

        if email is None or email.strip() == "":
            email = os.getenv("EBAY_EMAIL")
        if not email:
            raise ValueError("EBAY_EMAIL is missing. Add it to your .env file.")

        self._click_sign_in()
        self._enter_email(email)
        self.page.wait_for_timeout(3000)

    @allure.step("Enter email")
    def _enter_email(self, email: str) -> None:
        email_input = self.page.get_by_role(
            "textbox", name=re.compile(r"email|username", re.IGNORECASE)
        )

        expect(email_input).to_be_visible()
        email_input.fill(email)

    @allure.step("Click sign in")
    def _click_sign_in(self) -> None:
        sign_in_link = self.page.get_by_role(
            "link", name=re.compile(r"^Sign in$", re.IGNORECASE)
        )

        expect(sign_in_link).to_be_visible()
        sign_in_link.click()
