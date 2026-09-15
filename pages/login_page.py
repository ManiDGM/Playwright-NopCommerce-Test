"""UI interactions for the public login page."""

from playwright.sync_api import Page

from selectors.login_selectors import login_selectors


class LoginPage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    def navigate(self, return_url: str | None = None) -> None:
        url = f"{self.base_url}{login_selectors.LOGIN_URL_PATH}"
        if return_url:
            url = f"{url}?ReturnUrl={return_url}"
        self.page.goto(url)

    def fill_email(self, email: str) -> None:
        self.page.locator(login_selectors.EMAIL).fill(email)

    def fill_password(self, password: str) -> None:
        self.page.locator(login_selectors.PASSWORD).fill(password)

    def submit(self) -> None:
        self.page.locator(login_selectors.LOGIN_BUTTON).click()

    def login(self, email: str, password: str, return_url: str | None = None) -> None:
        self.navigate(return_url=return_url)
        self.fill_email(email)
        self.fill_password(password)
        self.submit()
