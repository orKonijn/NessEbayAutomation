# eBay UI Automation (Playwright + pytest) - Or Konijn

## Project overview
 automation eBay user flows:
- sign in
- advanced search with max-price filtering
- add items to cart and validate subtotal vs budget

The project uses a lightweight Page Object Model and keeps logic close to where it is used.

## Tech
- Python 3.10+
- Playwright (sync API)
- pytest
- allure-pytest
- python-dotenv

## Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e .
python -m playwright install chromium
```

## Environment variables
Create a local `.env` file (do not commit real secrets):

```dotenv
BASE_URL=https://www.ebay.com
BROWSER=chromium
HEADLESS=true

EBAY_EMAIL=your-email@example.com
EBAY_PASSWORD=your-password
```

## Run tests
```bash
pytest
```

Run one file:
```bash
pytest tests/test_ebay.py
```

## Run headed mode
```bash
pytest --headed
```

Or:
```bash
HEADLESS=false pytest
```

## Debug with Playwright Inspector
```bash
PWDEBUG=1 pytest -k test_add_items_to_cart
```

## Allure reports
Generate results:
```bash
pytest --alluredir=allure-results
```

Open report:
```bash
allure serve allure-results
```

## Project structure
```text
src/ebay/
  pages/
    advanced_search.py
    base_page.py
    cart_page.py
    ebay_site.py
    header_page.py
    item_page.py
    login_page.py
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
```

## Known eBay automation limitations
- eBay UI markup changes frequently and can vary by market/account.
- Some flows can trigger anti-bot friction (captcha/challenge).
- Search result ordering and listing cards are dynamic.
- Cart/checkout states can differ based on seller, shipping, and session state.

Keep tests smoke-level and focus on resilient selectors + business checks.
