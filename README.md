# eBay UI Automation with Playwright + Pytest

## Project overview
This repository automates core eBay user flows with **Playwright (Python)** and **pytest** using a Page Object Model (POM):
- Sign-in flow
- Advanced search and result filtering by max price
- Add item(s) to cart and validate subtotal constraints

The focus is maintainable, production-style test automation rather than brittle one-off scripts.

## Tech stack
- Python 3.10+
- Playwright (sync API)
- pytest
- allure-pytest
- python-dotenv (optional local credential loading)

## Project structure
```text
src/ebay/
  pages/
    base_page.py
    ebay_site.py
    header_page.py
    login_page.py
    advanced_search.py
    item_page.py
    cart_page.py
  utils/
    extract.py
    log.py
    place_holder.py
    price_parser.py
    random_option.py
tests/
  config/
    conftest.py
    playwright_config.py
  test_ebay.py
README.md
pyproject.toml
pytest.ini
```

## Installation
```bash
python -m venv .venv
source .venv/bin/activate # Windows: .venv\\Scripts\\activate
pip install -U pip
pip install -e .
```

## Environment variables

Create a local `.env` (or export env vars in your shell). Do not commit secrets.

Example `.env`:
```dotenv
BASE_URL=https://www.ebay.com
BROWSER=chromium
HEADLESS=true

EBAY_EMAIL=your-email@example.com
EBAY_PASSWORD=your-password
```
## Install Playwright browsers
```bash
python -m playwright install chromium
```

## Run tests
Run all tests:
```bash
pytest
```

Run a specific test file:
```bash
pytest tests/test_ebay.py
```

Run headed mode:
```bash
pytest --headed
```

Or via environment variable:
```bash
HEADLESS=false pytest
```

## Debugging
Debug mode with Playwright Inspector:
```bash
PWDEBUG=1 pytest -k test_search_lists_products
```

## Screenshots and traces
- Item/cart flows save screenshots in `artifacts/screenshots/`.
- This repository currently does **not** auto-enable tracing. If needed, add `context.tracing.start()` / `stop()` in `tests/config/conftest.py` for selected runs.

## Allure reporting
```bash
pytest --alluredir=allure-results
allure serve allure-results
```


## eBay automation limitations
eBay UI automation is inherently flaky in some scenarios due to:
- Dynamic markup and frequent A/B UI changes
- Bot detection, anti-automation friction, and geo/account-dependent flows
- Login challenges (captcha, verification prompts)
- Dynamic listing cards and unstable result ordering

Design assumptions used in this refactor:
- Primary support for eBay web desktop flow
- Credentials supplied via environment variables
- Tests are functional smoke-level flows, not strict deterministic data assertions across all markets