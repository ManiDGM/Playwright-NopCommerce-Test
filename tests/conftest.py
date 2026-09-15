"""Shared pytest fixtures for UI and API tests."""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from dotenv import load_dotenv
from playwright.sync_api import APIRequestContext, Browser, Playwright

from support.session_helpers import (
    build_storage_state_path,
    create_authenticated_request_context,
    login_as_admin_with_session,
    storage_state_exists,
)

load_dotenv()


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.environ.get("BASE_URL", "http://localhost:5000").rstrip("/")


@pytest.fixture(scope="session")
def admin_credentials() -> tuple[str, str]:
    email = os.environ.get("ADMIN_EMAIL")
    password = os.environ.get("ADMIN_PASSWORD")
    if not email or not password:
        pytest.skip("ADMIN_EMAIL and ADMIN_PASSWORD must be set in .env")
    return email, password


@pytest.fixture(scope="session")
def ensure_admin_session(browser: Browser, base_url: str, admin_credentials: tuple[str, str]):
    """Create admin storage_state once per session when missing."""
    if storage_state_exists("admin"):
        return build_storage_state_path("admin")

    email, password = admin_credentials
    context = browser.new_context(base_url=base_url)
    page = context.new_page()
    try:
        path = login_as_admin_with_session(
            page,
            base_url=base_url,
            email=email,
            password=password,
        )
    finally:
        context.close()
    return path


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict,
    ensure_admin_session,
) -> dict:
    browser_context_args["storage_state"] = str(ensure_admin_session)
    return browser_context_args


@pytest.fixture(scope="session")
def api_request_context(
    playwright: Playwright,
    base_url: str,
    ensure_admin_session,
) -> Generator[APIRequestContext, None, None]:
    context = create_authenticated_request_context(
        playwright,
        base_url=base_url,
    )
    yield context
    context.dispose()
