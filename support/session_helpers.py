"""Cookie-session and antiforgery helpers for nopCommerce admin automation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from playwright.sync_api import APIRequestContext, Page, Playwright

ANTIFORGERY_TOKEN_NAME = "__RequestVerificationToken"
_STORAGE_STATE_DIR = Path(__file__).resolve().parent.parent / ".auth"


def build_storage_state_path(role: str = "admin") -> Path:
    """Return the on-disk path for a role's Playwright storage_state file."""
    _STORAGE_STATE_DIR.mkdir(parents=True, exist_ok=True)
    return _STORAGE_STATE_DIR / f"{role.lower()}.json"


def storage_state_exists(role: str = "admin") -> bool:
    return build_storage_state_path(role).exists()


def extract_antiforgery_token(html: str) -> str:
    """Parse __RequestVerificationToken from admin page HTML."""
    patterns = (
        r'name=["\']__RequestVerificationToken["\'][^>]*value=["\']([^"\']+)["\']',
        r'value=["\']([^"\']+)["\'][^>]*name=["\']__RequestVerificationToken["\']',
    )
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1)
    raise ValueError(f"{ANTIFORGERY_TOKEN_NAME} not found in HTML")


def attach_antiforgery_token(data: dict[str, Any] | None, token: str) -> dict[str, Any]:
    """Add antiforgery token to a POST form body (mirrors addAntiForgeryToken in admin JS)."""
    payload = dict(data or {})
    payload[ANTIFORGERY_TOKEN_NAME] = token
    return payload


def fetch_antiforgery_token(request: APIRequestContext, url: str) -> str:
    """GET an admin page and return its antiforgery token."""
    response = request.get(url)
    if not response.ok:
        raise RuntimeError(f"Failed to fetch antiforgery page {url}: HTTP {response.status}")
    return extract_antiforgery_token(response.text())


def fetch_antiforgery_token_from_page(page: Page, url: str) -> str:
    """Navigate to an admin page and return its antiforgery token."""
    page.goto(url)
    return extract_antiforgery_token(page.content())


def login_as_admin_with_session(
    page: Page,
    *,
    base_url: str,
    email: str,
    password: str,
    role: str = "admin",
    return_url: str | None = None,
) -> Path:
    """
    Log in at /login via UI, wait for admin area, and persist storage_state.

    Reuses an existing storage_state file when present unless credentials change
    requires a fresh login (delete .auth/{role}.json to force re-login).
    """
    from pages.login_page import LoginPage

    storage_path = build_storage_state_path(role)
    if storage_path.exists():
        return storage_path

    login_page = LoginPage(page, base_url)
    login_page.login(email, password, return_url=return_url)

    page.context.storage_state(path=str(storage_path))
    return storage_path


def seed_browser_auth(role: str = "admin") -> dict[str, str]:
    """
    Return kwargs for browser.new_context / pytest browser_context_args.

    Example:
        context = browser.new_context(base_url=base_url, **seed_browser_auth())
    """
    storage_path = build_storage_state_path(role)
    if not storage_path.exists():
        raise FileNotFoundError(
            f"Storage state not found at {storage_path}. "
            "Call login_as_admin_with_session first."
        )
    return {"storage_state": str(storage_path)}


def create_authenticated_request_context(
    playwright: Playwright,
    *,
    base_url: str,
    role: str = "admin",
) -> APIRequestContext:
    """Create an APIRequestContext that reuses cookie auth from storage_state."""
    storage_path = build_storage_state_path(role)
    if not storage_path.exists():
        raise FileNotFoundError(
            f"Storage state not found at {storage_path}. "
            "Run login_as_admin_with_session first (see tests/conftest.py ensure_admin_session)."
        )
    return playwright.request.new_context(
        base_url=base_url.rstrip("/"),
        storage_state=str(storage_path),
    )
