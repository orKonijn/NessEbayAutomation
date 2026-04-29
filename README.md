# eBay Playwright + Allure (Python)

Starter repo for web UI automation on eBay using **Playwright + Pytest + Allure**.

## 1) Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
python -m playwright install chromium
```

## 2) Run tests

```bash
pytest
```

Run headed mode (non-headless):

```bash
pytest --headed
```

Or configure via env var:

```bash
HEADLESS=false pytest
```

## 3) Generate Allure report

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

> If `allure` command is missing, install Allure CLI:
>
> - macOS: `brew install allure`
> - Windows: `scoop install allure`
> - Linux: use package manager or download from Allure releases.

## 4) Project layout

- `src/ebay/pages/`: Page Objects
- `tests/`: Test cases and fixtures
- `pyproject.toml`: Python dependencies and packaging config

## Notes

- Default target URL is `https://www.ebay.com`.
- Override with environment variable:

```bash