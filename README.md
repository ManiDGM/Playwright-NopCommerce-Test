# Playwright-NopCommerce-Test

Playwright + pytest automation for nopCommerce admin catalog features.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
playwright install
copy .env.example .env          # then set BASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD
```

## Run tests

```bash
pytest                          # all tests under tests/
pytest tests/e2e/ui             # UI specs only
pytest tests/e2e/api            # API specs only
```

UI/API fixtures in `tests/conftest.py` load `.env`, create admin `storage_state` once per session (`.auth/admin.json`), and reuse it for browser contexts and `api_request_context`.

## Project layout

| Layer | Path | Purpose |
|-------|------|---------|
| Selectors | `selectors/` | Stable DOM locators (`#id`, `name=`, role+label) |
| Pages | `pages/` | UI interaction only |
| Actions | `actions/` | UI business flows |
| API | `api/endpoints`, `clients`, `actions`, `types` | Admin AJAX/MVC POST wrappers |
| Support | `support/session_helpers.py` | Cookie session + antiforgery |
| Specs | `tests/e2e/ui`, `tests/e2e/api` | Assertions + `log_data` only |

Catalog feature modules live under `*/catalog/` (Wave 1 agents add products, categories, manufacturers, product_reviews).

## Selector convention

nopCommerce does **not** use `data-testid`. Prefer stable attributes from admin/public views:

- `#Email`, `#Password` on `/login`
- `#Name`, `#search-categories`, `#categories-grid` on admin list/create forms

Centralize every selector in `selectors/` modules — never inline in specs.

## Auth pattern (nopCommerce)

1. UI login at `/login` → persist Playwright `storage_state` (`.auth/admin.json`).
2. API clients reuse the same cookies via `api_request_context` or `create_authenticated_request_context`.
3. Before admin POSTs: GET a list page, parse `__RequestVerificationToken`, attach with `attach_antiforgery_token`.

No bearer `POST_TOKEN` — cookie session + antiforgery only.

## Imports for feature agents

```python
import actions
import pages
import selectors
from support.session_helpers import (
    attach_antiforgery_token,
    extract_antiforgery_token,
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
