"""Stable selectors for the public /login page."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LoginSelectors:
    EMAIL: str = "#Email"
    PASSWORD: str = "#Password"
    REMEMBER_ME: str = "#RememberMe"
    LOGIN_BUTTON: str = "button.login-button"
    LOGIN_URL_PATH: str = "/login"


login_selectors = LoginSelectors()
