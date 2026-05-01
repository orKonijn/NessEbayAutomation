import re
import os
from pathlib import Path

import allure
from dotenv import load_dotenv
from playwright.sync_api import Page, expect


class LoginPage:

    def __init__(self, page: Page) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        load_dotenv(repo_root / ".env")
        self.page = page

    @allure.step("Login with email")
    def login(self, email: str | None = None, password: str | None = None) -> None:

        if email is None or email.strip() == "":
            email = os.getenv("EBAY_EMAIL")
        if not email:
            raise ValueError("EBAY_EMAIL is missing. Add it to your .env file.")
        if password is None or email.strip() == "":
            password = os.getenv("EBAY_PASSWORD")
        if not password:
            raise ValueError("EBAY_PASSWORD is missing. Add it to your .env file.")

        self._click_sign_in()
        self.page.wait_for_timeout(3000)
        self._enter_email(email)
        self.page.wait_for_timeout(3000)
        self._click_continue()
        self.page.wait_for_timeout(3000)
        self._enter_password(password)
        self.page.wait_for_timeout(3000)
        self._click_login_with_password()
        self.page.wait_for_timeout(3000)

    @allure.step("Enter email")
    def _enter_email(self, email: str) -> None:
        email_input = self.page.get_by_test_id("userid")

        expect(email_input).to_be_visible()
        email_input.fill(email)
        expect(email_input).to_have_value(email)

    @allure.step("Click sign in")
    def _click_sign_in(self) -> None:
        sign_in_link = self.page.get_by_role(
            "link", name=re.compile(r"^Sign in$", re.IGNORECASE)
        )

        expect(sign_in_link).to_be_visible()
        sign_in_link.click()

    @allure.step("Click Continue to sign in")
    def _click_continue(self) -> None:
        continue_button = self.page.get_by_test_id("signin-continue-btn")

        expect(continue_button).to_be_visible()
        continue_button.click()

    @allure.step("Enter password")
    def _enter_password(self, password: str) -> None:
        password_input = self.page.get_by_test_id("pass")

        expect(password_input).to_be_visible()
        password_input.fill(password)
        expect(password_input).to_have_value(password)

    @allure.step("login with email and password")
    def _click_login_with_password(self) -> None:
        sgn_button = self.page.get_by_test_id("sgnBt")

        expect(sgn_button).to_be_visible()
        expect(sgn_button).to_be_enabled()
        sgn_button.click()
