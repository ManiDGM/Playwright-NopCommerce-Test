"""Business flows for admin authentication."""

import os

from playwright.sync_api import Page

from pages.login_page import LoginPage
from support.session_helpers import login_as_admin_with_session


class LoginActions:
    def __init__(self, page: Page, base_url: str | None = None) -> None:
        self.page = page
        self.base_url = (base_url or os.environ.get("BASE_URL", "http://localhost:5000")).rstrip("/")
        self.login_page = LoginPage(page, self.base_url)

    def login_as_admin(
        self,
        email: str | None = None,
        password: str | None = None,
        return_url: str | None = None,
    ) -> None:
        email = email or os.environ["ADMIN_EMAIL"]
        password = password or os.environ["ADMIN_PASSWORD"]
        self.login_page.login(email, password, return_url=return_url)

    def login_as_admin_with_session(
        self,
        email: str | None = None,
        password: str | None = None,
        return_url: str | None = None,
    ):
        email = email or os.environ["ADMIN_EMAIL"]
        password = password or os.environ["ADMIN_PASSWORD"]
        return login_as_admin_with_session(
            self.page,
            base_url=self.base_url,
            email=email,
            password=password,
            return_url=return_url,
        )
