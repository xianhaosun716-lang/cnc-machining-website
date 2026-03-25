@echo off
setlocal enabledelayedexpansion

cd /d %~dp0

echo [1/6] Checking Python...
where python >nul 2>nul
if errorlevel 1 (
  echo Python not found. Please install Python 3.11+ from python.org
  pause
  exit /b 1
)

echo [2/6] Creating virtual environment...
if not exist .venv (
  python -m venv .venv
  if errorlevel 1 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
  )
)

echo [3/6] Activating virtual environment...
call .venv\Scripts\activate
if errorlevel 1 (
  echo Failed to activate virtual environment.
  pause
  exit /b 1
)

echo [4/6] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed.
  pause
  exit /b 1
)

echo [5/6] Building exe with PyInstaller...
pyinstaller --noconfirm ChatHelper.spec
if errorlevel 1 (
  echo PyInstaller build failed.
  pause
  exit /b 1
)

echo [6/6] Preparing deliverable package...
python package_release.py
if errorlevel 1 (
  echo Packaging release folder failed.
  pause
  exit /b 1
)

echo.
echo Build complete.
echo Deliverable folder: release\ChatHelper-Windows
echo Zip file: release\ChatHelper-Windows.zip
pause
