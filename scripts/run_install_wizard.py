"""Automate the nopCommerce first-run install wizard via Playwright.

Used by setup.bat after Docker is up. Safe to re-run: skips if already installed.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"

# Match docker-compose.yml (SQL reachable as service name on the Docker network)
SQL_SERVER = "nopcommerce_database"
SQL_USER = "sa"
SQL_PASSWORD = "nopCommerce_db_password"
SQL_DATABASE = "nopCommerce"

DEFAULT_ADMIN_EMAIL = "admin@yourstore.com"
DEFAULT_ADMIN_PASSWORD = "Admin@123456"
PLACEHOLDER_PASSWORDS = {"", "your_admin_password", "changeme"}

STORE_READY_TIMEOUT_MS = 300_000  # 5 min — SQL Server + web cold start
INSTALL_POST_TIMEOUT_MS = 600_000  # 10 min — schema + seed
RESTART_REDIRECT_TIMEOUT_MS = 180_000  # 3 min — app restart after install


def _load_env() -> tuple[str, str, str]:
    load_dotenv(ENV_PATH, override=True)
    base_url = (os.environ.get("BASE_URL") or "http://localhost").rstrip("/")
    email = (os.environ.get("ADMIN_EMAIL") or DEFAULT_ADMIN_EMAIL).strip()
    password = (os.environ.get("ADMIN_PASSWORD") or "").strip()
    if password.lower() in PLACEHOLDER_PASSWORDS:
        password = DEFAULT_ADMIN_PASSWORD
    return base_url, email, password


def _upsert_env(email: str, password: str) -> None:
    """Ensure .env has the admin credentials used for install."""
    if not ENV_PATH.exists():
        example = ROOT / ".env.example"
        if example.exists():
            ENV_PATH.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            ENV_PATH.write_text(
                f"BASE_URL=http://localhost\nADMIN_EMAIL={email}\nADMIN_PASSWORD={password}\n",
                encoding="utf-8",
            )

    lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
    keys = {"ADMIN_EMAIL": email, "ADMIN_PASSWORD": password, "BASE_URL": "http://localhost"}
    seen: set[str] = set()
    out: list[str] = []
    for line in lines:
        matched = False
        for key, value in keys.items():
            if re.match(rf"^\s*{re.escape(key)}\s*=", line, flags=re.IGNORECASE):
                out.append(f"{key}={value}")
                seen.add(key)
                matched = True
                break
        if not matched:
            out.append(line)
    for key, value in keys.items():
        if key not in seen:
            out.append(f"{key}={value}")
    ENV_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")


def _wait_for_store(page, base_url: str) -> None:
    print(f"Waiting for store at {base_url} ...")
    deadline_errors: list[str] = []
    page.set_default_navigation_timeout(STORE_READY_TIMEOUT_MS)
    try:
        page.goto(base_url, wait_until="domcontentloaded", timeout=STORE_READY_TIMEOUT_MS)
    except PlaywrightTimeoutError as exc:
        deadline_errors.append(str(exc))
        # Retry once — SQL/web often need a second wave after compose up
        page.goto(base_url, wait_until="domcontentloaded", timeout=STORE_READY_TIMEOUT_MS)
    # Prefer install form or a settled homepage
    try:
        page.locator("#AdminEmail, #Email, .header, .master-wrapper-page").first.wait_for(
            state="visible", timeout=60_000
        )
    except PlaywrightTimeoutError:
        if deadline_errors:
            raise RuntimeError(
                f"Store did not become ready at {base_url}. Is Docker running?\n"
                + "\n".join(deadline_errors)
            ) from None
        raise


def _already_installed(page) -> bool:
    if page.locator("#AdminEmail").count() == 0:
        return True
    if "/install" not in page.url.lower() and page.locator("#installation-form").count() == 0:
        return True
    return False


def _fill_and_install(page, email: str, password: str) -> None:
    print("Filling install wizard ...")
    page.locator("#AdminEmail").fill(email)
    page.locator("#AdminPassword").fill(password)
    page.locator("#ConfirmPassword").fill(password)

    if page.locator("#SubscribeNewsletters").count():
        page.locator("#SubscribeNewsletters").uncheck()

    if page.locator("#InstallSampleData").count():
        # Faster first install; catalog tests create their own data
        page.locator("#InstallSampleData").uncheck()

    # DataProvider defaults to SqlServer (enum ToString value)
    if page.locator("#DataProvider").count():
        try:
            page.locator("#DataProvider").select_option(value="SqlServer")
        except Exception:
            # Fallback: first option that looks like SQL Server by visible text
            options = page.locator("#DataProvider option")
            for i in range(options.count()):
                text = options.nth(i).inner_text()
                if re.search(r"sql", text, re.I):
                    page.locator("#DataProvider").select_option(index=i)
                    break

    page.locator("#CreateDatabaseIfNotExists").check()

    if page.locator("#ConnectionStringRaw").is_checked():
        page.locator("#ConnectionStringRaw").uncheck()

    if page.locator("#IntegratedSecurity").is_checked():
        page.locator("#IntegratedSecurity").uncheck()

    page.locator("#ServerName").fill(SQL_SERVER)
    page.locator("#DatabaseName").fill(SQL_DATABASE)
    page.locator("#Username").fill(SQL_USER)
    page.locator("#Password").fill(SQL_PASSWORD)

    print("Submitting install (this can take several minutes) ...")
    page.set_default_timeout(INSTALL_POST_TIMEOUT_MS)
    page.locator("button.btn-install[type=submit]").click()
    page.wait_for_load_state("domcontentloaded", timeout=INSTALL_POST_TIMEOUT_MS)

    error_items = page.locator(".message-error li")
    if error_items.count() > 0:
        messages = [m.strip() for m in error_items.all_inner_texts() if m.strip()]
        # Empty <li> nodes can appear during post-install restart; ignore those.
        if messages:
            raise RuntimeError(
                "Install wizard reported errors:\n" + "\n".join(messages)
            )

    print("Waiting for post-install redirect off /install ...")
    try:
        page.wait_for_function(
            "() => !window.location.pathname.toLowerCase().includes('install')",
            timeout=RESTART_REDIRECT_TIMEOUT_MS,
        )
    except PlaywrightTimeoutError:
        # Install may have finished but restart hung — fail only if form still interactive
        if page.locator("#AdminEmail").count() and page.locator("#AdminEmail").is_visible():
            raise RuntimeError(
                "Install did not leave /install. Check Docker logs: "
                "docker compose logs nopcommerce_web"
            ) from None
        print("Warning: redirect timed out; install may still have completed.")

def main() -> int:
    base_url, email, password = _load_env()
    _upsert_env(email, password)
    # Reload after upsert
    base_url, email, password = _load_env()

    print(f"BASE_URL={base_url}")
    print(f"ADMIN_EMAIL={email}")
    print("ADMIN_PASSWORD=(set in .env)")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        try:
            _wait_for_store(page, base_url)
            if _already_installed(page):
                print("nopCommerce already installed — skipping wizard.")
                return 0
            _fill_and_install(page, email, password)
            print("Install wizard completed successfully.")
            return 0
        except Exception as exc:  # noqa: BLE001 — top-level CLI
            print(f"[ERROR] {exc}", file=sys.stderr)
            try:
                shot = ROOT / "test-results" / "install-wizard-failure.png"
                shot.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(shot), full_page=True)
                print(f"Screenshot saved: {shot}", file=sys.stderr)
            except Exception:  # noqa: BLE001
                pass
            return 1
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    raise SystemExit(main())
