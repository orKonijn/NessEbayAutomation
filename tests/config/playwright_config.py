import os
from dataclasses import dataclass


@dataclass(frozen=True)
class PlaywrightConfig:
    base_url: str
    browser_name: str
    headless: bool

    @staticmethod
    def from_env() -> "PlaywrightConfig":
        headless_env = os.getenv("HEADLESS", "true").strip().lower()
        headless = headless_env not in {"0", "false", "no", "off"}

        return PlaywrightConfig(
            base_url=os.getenv("BASE_URL", "https://sandbox.ebay.com/"),
            browser_name=os.getenv("BROWSER", "chromium"),
            headless=headless,
        )
