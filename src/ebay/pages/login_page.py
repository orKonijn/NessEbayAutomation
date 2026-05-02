import logging
import os
import re
from pathlib import Path

import allure
from dotenv import load_dotenv
from playwright.sync_api import Error, Page, expect

logger = logging.getLogger(__name__)


def mask_email(email: str) -> str:
    if "@" not in email:
        return "***"

    username, domain = email.split("@", maxsplit=1)

    if len(username) <= 2:
        masked_username = username[0] + "***"
    else:
        masked_username = f"{username[:2]}***"

    return f"{masked_username}@{domain}"


class LoginPage:
    def __init__(self, page: Page) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        load_dotenv(repo_root / ".env")

        self.page = page
        self.screenshot_dir = Path("artifacts/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    @allure.step("Login with email")
    def login(self, email: str | None = None, password: str | None = None) -> None:
        email, password = self._resolve_credentials(email=email, password=password)
        masked_email = mask_email(email)

        logger.info("Starting login flow | email=%s", masked_email)

        allure.dynamic.parameter("email", masked_email)

        allure.attach(
            f"Email: {masked_email}\nCurrent URL before login: {self.page.url}",
            name="Login context",
            attachment_type=allure.attachment_type.TEXT,
        )

        try:
            self._click_sign_in()
            self._enter_email(email)
            self._click_continue()
            self._enter_password(password)
            self._click_login_with_password()

            logger.info("Login flow submitted successfully | email=%s", masked_email)

            allure.attach(
                f"Login submitted successfully\nEmail: {masked_email}\nCurrent URL: {self.page.url}",
                name="Login result",
                attachment_type=allure.attachment_type.TEXT,
            )

        except Exception as exc:
            logger.exception("Login flow failed | email=%s", masked_email)

            allure.attach(
                str(exc),
                name="Login error",
                attachment_type=allure.attachment_type.TEXT,
            )

            screenshot_path = self._save_login_failure_screenshot()

            if screenshot_path:
                allure.attach.file(
                    screenshot_path,
                    name="Login failure screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )

            raise

    def _resolve_credentials(
        self,
        email: str | None,
        password: str | None,
    ) -> tuple[str, str]:
        if email is None or email.strip() == "":
            email = os.getenv("EBAY_EMAIL")

        if not email:
            logger.error("EBAY_EMAIL is missing.")
            raise ValueError("EBAY_EMAIL is missing. Add it to your .env file.")

        if password is None or password.strip() == "":
            password = os.getenv("EBAY_PASSWORD")

        if not password:
            logger.error("EBAY_PASSWORD is missing.")
            raise ValueError("EBAY_PASSWORD is missing. Add it to your .env file.")

        logger.debug("Login credentials resolved | email=%s", mask_email(email))

        return email, password

    @allure.step("Click sign in")
    def _click_sign_in(self) -> None:
        logger.info("Clicking Sign in link.")

        sign_in_link = self.page.get_by_role(
            "link",
            name=re.compile(r"^Sign in$", re.IGNORECASE),
        )

        expect(sign_in_link).to_be_visible(timeout=10_000)
        sign_in_link.click()

        logger.info("Clicked Sign in link | current_url=%s", self.page.url)

    @allure.step("Enter email")
    def _enter_email(self, email: str) -> None:
        masked_email = mask_email(email)

        logger.info("Entering email | email=%s", masked_email)

        email_input = self.page.get_by_test_id("userid")

        expect(email_input).to_be_visible(timeout=10_000)
        email_input.fill(email)
        expect(email_input).to_have_value(email)

        allure.attach(
            f"Entered email: {masked_email}",
            name="Email entered",
            attachment_type=allure.attachment_type.TEXT,
        )

        logger.info("Email entered successfully | email=%s", masked_email)

    @allure.step("Click Continue to sign in")
    def _click_continue(self) -> None:
        logger.info("Clicking Continue button.")

        continue_button = self.page.get_by_test_id("signin-continue-btn")

        expect(continue_button).to_be_visible(timeout=10_000)
        expect(continue_button).to_be_enabled(timeout=10_000)
        continue_button.click()

        logger.info("Clicked Continue button | current_url=%s", self.page.url)

    @allure.step("Enter password")
    def _enter_password(self, password: str) -> None:
        logger.info("Entering password.")

        password_input = self.page.get_by_test_id("pass")

        expect(password_input).to_be_visible(timeout=10_000)
        password_input.fill(password)
        expect(password_input).to_have_value(password)

        allure.attach(
            "Password was entered. Value is hidden for security.",
            name="Password entered",
            attachment_type=allure.attachment_type.TEXT,
        )

        logger.info("Password entered successfully.")

    @allure.step("Login with email and password")
    def _click_login_with_password(self) -> None:
        logger.info("Clicking final login button.")

        sign_in_button = self.page.get_by_test_id("sgnBt")

        expect(sign_in_button).to_be_visible(timeout=10_000)
        expect(sign_in_button).to_be_enabled(timeout=10_000)
        sign_in_button.click()

        logger.info("Clicked final login button | current_url=%s", self.page.url)

    def _save_login_failure_screenshot(self) -> str:
        screenshot_path = self.screenshot_dir / "login-failure.png"

        try:
            self.page.screenshot(path=str(screenshot_path), full_page=True)

            logger.info("Saved login failure screenshot | path=%s", screenshot_path)

            return str(screenshot_path)

        except Error:
            logger.exception(
                "Failed to save login failure screenshot | path=%s",
                screenshot_path,
            )

            return ""
