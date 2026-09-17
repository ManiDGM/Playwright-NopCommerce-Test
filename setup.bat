@echo off
REM One-shot setup for Playwright-NopCommerce-Test:
REM   - creates .venv and installs Python + Playwright deps
REM   - creates .env from .env.example (if missing)
REM   - starts nopCommerce via local docker-compose.yml
REM   - automates the install wizard (SQL + admin from .env)
REM
REM Usage (from this repo root, or double-click):
REM   setup.bat

setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo ============================================
echo  Playwright-NopCommerce-Test — full setup
echo ============================================
echo.

REM ---- Prerequisites ----
where python >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python is not installed or not on PATH. Install Python 3.11+, then retry.
  goto :fail
)

where docker >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Docker is not installed or not on PATH. Install Docker Desktop, then retry.
  goto :fail
)

if not exist "docker-compose.yml" (
  echo [ERROR] docker-compose.yml not found in this repo:
  echo   %cd%
  echo Restore it from the project, then retry.
  goto :fail
)

REM ---- 1. Virtual environment ----
echo [1/5] Python virtual environment...
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
  if errorlevel 1 (
    echo [ERROR] Failed to create .venv
    goto :fail
  )
  echo   Created .venv
) else (
  echo   .venv already exists — skipping create
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
  echo [ERROR] Failed to activate .venv
  goto :fail
)

REM ---- 2. Dependencies ----
echo.
echo [2/5] Installing Python packages and Playwright browsers...
python -m pip install --upgrade pip
if errorlevel 1 goto :fail
pip install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] pip install failed
  goto :fail
)
playwright install chromium
if errorlevel 1 (
  echo [ERROR] playwright install failed
  goto :fail
)
echo   Dependencies installed

REM ---- 3. Environment file ----
echo.
echo [3/5] Environment file (.env)...
if not exist ".env" (
  if not exist ".env.example" (
    echo [ERROR] .env.example is missing
    goto :fail
  )
  copy /Y ".env.example" ".env" >nul
  echo   Created .env from .env.example
) else (
  echo   .env already exists — not overwriting
)

REM ---- 4. Docker (nopCommerce) ----
echo.
echo [4/5] Starting nopCommerce Docker stack...
docker compose up -d
if errorlevel 1 (
  echo [ERROR] Docker Compose failed. Is Docker Desktop running?
  goto :fail
)

REM ---- 5. Install wizard ----
echo.
echo [5/5] Running install wizard automation...
python scripts\run_install_wizard.py
if errorlevel 1 (
  echo [ERROR] Install wizard automation failed.
  goto :fail
)

echo.
echo ============================================
echo  Setup complete
echo ============================================
echo.
echo Store:  http://localhost
echo Admin:  http://localhost/admin
echo.
echo Admin credentials are in .env ^(ADMIN_EMAIL / ADMIN_PASSWORD^).
echo.
echo Next steps:
echo   1. Activate venv and run tests:
echo        .venv\Scripts\activate
echo        pytest
echo.
echo Stop Docker (from this repo root):
echo   docker compose down
echo.
exit /b 0

:fail
echo.
echo Setup failed. Fix the error above and run setup.bat again.
exit /b 1
