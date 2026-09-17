# Playwright-NopCommerce-Test

Playwright + pytest automation for nopCommerce admin catalog features.

## Project structure

```text
Playwright-NopCommerce-Test/
├── setup.bat                    # One-shot: .venv, deps, .env, Docker, install wizard
├── docker-compose.yml           # nopCommerce + SQL Server (official images)
├── scripts/
│   └── run_install_wizard.py    # Automates first-run install wizard
├── .env.example                 # Required env vars (copy to .env)
├── pytest.ini
├── requirements.txt
├── actions/                     # UI business flows
│   ├── login_actions.py
│   └── catalog/
│       ├── categories_actions.py
│       ├── manufacturers_actions.py
│       ├── products_actions.py
│       └── product_reviews_actions.py
├── api/                         # API layers (endpoints → clients → actions → types)
│   ├── endpoints/catalog/
│   ├── clients/catalog/
│   ├── actions/catalog/
│   └── types/catalog/
├── pages/                       # UI interaction only
│   ├── login_page.py
│   └── catalog/
├── selectors/                   # Locators only (#id, name=, role+label)
│   ├── common_selectors.py
│   ├── login_selectors.py
│   └── catalog/
├── scenarios/catalog/           # Gherkin feature files
├── support/
│   └── session_helpers.py       # Cookie session + antiforgery
└── tests/
    ├── conftest.py              # Shared fixtures (env, auth, browser)
    └── e2e/
        ├── ui/                  # UI specs
        └── api/                 # API specs
```

| Layer | Path | Purpose |
|-------|------|---------|
| Selectors | `selectors/` | Stable DOM locators |
| Pages | `pages/` | UI interaction only (no assertions) |
| Actions | `actions/` | UI business flows |
| API | `api/endpoints`, `clients`, `actions`, `types` | Admin AJAX/MVC wrappers |
| Support | `support/session_helpers.py` | Cookie session + antiforgery |
| Specs | `tests/e2e/ui`, `tests/e2e/api` | Assertions + `log_data` only |

## Prerequisites

* Python 3.11+
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (to run nopCommerce locally)

All test config and the Docker stack live in this repo (`.env`, `docker-compose.yml`, selectors, pages, etc.). No sibling nopCommerce source clone is required. Compose maps the store to host port **80** (`http://localhost`) using the official image `nopcommerceteam/nopcommerce:4.90.8`.

## Quick start (one command)

From this project's root (Command Prompt), or double-click the file:

```bat
setup.bat
```

This single script:

1. Creates `.venv` (if missing)
2. Installs `requirements.txt` and Playwright Chromium
3. Creates `.env` from `.env.example` (if missing)
4. Starts nopCommerce via this repo's `docker-compose.yml`
5. Automates the install wizard (SQL Server + admin from `.env`) — skips if already installed

Then open:

* Store: [http://localhost](http://localhost)
* Admin: [http://localhost/admin](http://localhost/admin)

### Install wizard (automated)

`setup.bat` runs [`scripts/run_install_wizard.py`](scripts/run_install_wizard.py), which fills the wizard with:

| Setting  | Value                     |
|----------|---------------------------|
| Server   | `nopcommerce_database`    |
| Database | `nopCommerce` (created if missing) |
| User     | `sa`                      |
| Password | `nopCommerce_db_password` |

Admin email/password come from `.env` (defaults in `.env.example`):

| Variable | Default |
|----------|---------|
| `BASE_URL` | `http://localhost` |
| `ADMIN_EMAIL` | `admin@yourstore.com` |
| `ADMIN_PASSWORD` | `Admin@123456` |

Change those values in `.env` before re-running setup on a fresh stack if you want different admin credentials. First install can take several minutes while SQL Server starts and nopCommerce creates the database.

Stop the Docker stack (from this repo root):

```bat
docker compose down
```

To wipe the store and re-run the wizard, remove containers **and** volumes, then run `setup.bat` again:

```bat
docker compose down -v
setup.bat
```

### Manual setup (optional)

If you prefer step-by-step instead of `setup.bat`:

```bat
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
copy .env.example .env
docker compose up -d
python scripts\run_install_wizard.py
```

## Run tests

```powershell
pytest                          # all tests under tests/
pytest tests/e2e/ui             # UI specs only (headless)
pytest tests/e2e/api            # API specs only
```

### UI tests with a visible browser

```powershell
pytest tests/e2e/ui --headed
```

Optional:

```powershell
pytest tests/e2e/ui --headed --slowmo 300   # slow down actions (ms)
pytest tests/e2e/ui --headed -k categories  # one feature by name
```

UI/API fixtures in `tests/conftest.py` load `.env`, create admin `storage_state` once per session (`.auth/admin.json`), and reuse it for browser contexts and `api_request_context`.

## Auth pattern (nopCommerce)

1. UI login at `/login` → persist Playwright `storage_state` (`.auth/admin.json`).
2. API clients reuse the same cookies via `api_request_context`.
3. Before admin POSTs: GET a list page, parse `__RequestVerificationToken`, attach with `attach_antiforgery_token`.

No bearer `POST_TOKEN` — cookie session + antiforgery only.

## Selector convention

nopCommerce does **not** use `data-testid`. Prefer stable attributes:

* `#Email`, `#Password` on `/login`
* `#Name`, `#search-categories`, `#categories-grid` on admin list/create forms

Centralize every selector in `selectors/` modules — never inline in specs.

## Imports

```python
import actions
import pages
import selectors
from support.session_helpers import (
    attach_antiforgery_token,
    fetch_antiforgery_token,
    login_as_admin_with_session,
)

# UI
actions.LoginActions(page).login_as_admin_with_session()
selectors.login_selectors.EMAIL

# API POST body
token = fetch_antiforgery_token(api_request_context, "/Admin/Category/List")
payload = attach_antiforgery_token({"SearchCategoryName": "test"}, token)
```
