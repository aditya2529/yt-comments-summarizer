@echo off
setlocal enabledelayedexpansion
color 0B
title CommentLens - First-Time Setup

echo.
echo  ============================================================
echo    CommentLens ^- First-Time Setup
echo  ============================================================
echo.
echo  This will set up everything you need to run CommentLens.
echo  It should take about 2-5 minutes.
echo.
pause

:: ----------------------------------------------------------------
:: STEP 1 - Check Python 3.11+
:: ----------------------------------------------------------------
echo.
color 0E
echo  [Step 1/4]  Checking for Python 3.11 or newer...
echo.
color 0B

python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo  ERROR: Python was not found on this computer.
    echo.
    echo  Please do the following:
    echo    1. A browser window will open to the Python download page.
    echo    2. Click the big yellow "Download Python" button.
    echo    3. Run the installer.
    echo    4. IMPORTANT: On the first screen of the installer,
    echo       tick the box that says "Add Python to PATH"
    echo       before clicking Install Now.
    echo    5. After installation is complete, re-run SETUP.bat.
    echo.
    start "" "https://www.python.org/downloads/"
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%V in ('python --version 2^>^&1') do set PYVER=%%V
for /f "tokens=1,2 delims=." %%A in ("!PYVER!") do (
    set PY_MAJOR=%%A
    set PY_MINOR=%%B
)

if !PY_MAJOR! LSS 3 (
    color 0C
    echo  ERROR: Python !PYVER! found, but version 3.11+ is required.
    echo  Please download a newer version from https://www.python.org/downloads/
    start "" "https://www.python.org/downloads/"
    pause
    exit /b 1
)
if !PY_MAJOR! EQU 3 if !PY_MINOR! LSS 11 (
    color 0C
    echo  ERROR: Python !PYVER! found, but version 3.11+ is required.
    echo  Please download a newer version from https://www.python.org/downloads/
    start "" "https://www.python.org/downloads/"
    pause
    exit /b 1
)

color 0A
echo  OK  Python !PYVER! found.

:: ----------------------------------------------------------------
:: STEP 2 - Check Node.js 18+
:: ----------------------------------------------------------------
echo.
color 0E
echo  [Step 2/4]  Checking for Node.js 18 or newer...
echo.
color 0B

node --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo  ERROR: Node.js was not found on this computer.
    echo.
    echo  Please do the following:
    echo    1. A browser window will open to the Node.js download page.
    echo    2. Click the button labelled "LTS" (Recommended for Most Users).
    echo    3. Run the installer and accept all defaults.
    echo    4. After installation is complete, re-run SETUP.bat.
    echo.
    start "" "https://nodejs.org/en/download/"
    pause
    exit /b 1
)

for /f "tokens=1 delims=v" %%A in ('node --version') do set NODEVER=%%A
for /f "tokens=1 delims=." %%A in ("!NODEVER!") do set NODE_MAJOR=%%A

if !NODE_MAJOR! LSS 18 (
    color 0C
    echo  ERROR: Node.js !NODEVER! found, but version 18+ is required.
    echo  Please download a newer version from https://nodejs.org/en/download/
    start "" "https://nodejs.org/en/download/"
    pause
    exit /b 1
)

color 0A
echo  OK  Node.js !NODEVER! found.

:: ----------------------------------------------------------------
:: STEP 3 - Install dependencies
:: ----------------------------------------------------------------
echo.
color 0E
echo  [Step 3/4]  Installing dependencies (this may take a minute)...
echo.
color 0B

echo  Installing Python packages...
cd /d "%~dp0backend"
pip install -r requirements.txt
if errorlevel 1 (
    color 0C
    echo.
    echo  ERROR: Failed to install Python packages.
    echo  Make sure you are connected to the internet and try again.
    pause
    exit /b 1
)
color 0A
echo  OK  Python packages installed.
echo.
color 0B

echo  Installing Node.js packages...
cd /d "%~dp0frontend"
call npm install
if errorlevel 1 (
    color 0C
    echo.
    echo  ERROR: Failed to install Node.js packages.
    echo  Make sure you are connected to the internet and try again.
    pause
    exit /b 1
)
color 0A
echo  OK  Node.js packages installed.

:: ----------------------------------------------------------------
:: STEP 4 - API Keys
:: ----------------------------------------------------------------
echo.
color 0E
echo  [Step 4/4]  Setting up your API keys...
echo.
color 0B
echo  You need two API keys to use CommentLens:
echo.
echo    1. YOUTUBE_API_KEY   - Free from Google.
echo    2. ANTHROPIC_API_KEY - From Anthropic (costs about $0.01 per summary).
echo.
echo  If you do not have these keys yet, please open HOW_TO_USE.txt
echo  for step-by-step instructions before continuing.
echo.
pause

:enter_youtube_key
echo.
color 0B
set /p YOUTUBE_KEY="  Paste your YOUTUBE_API_KEY and press Enter: "
if "!YOUTUBE_KEY!"=="" (
    color 0C
    echo  The YouTube API key cannot be blank. Please try again.
    goto enter_youtube_key
)

:enter_anthropic_key
echo.
set /p ANTHROPIC_KEY="  Paste your ANTHROPIC_API_KEY and press Enter: "
if "!ANTHROPIC_KEY!"=="" (
    color 0C
    echo  The Anthropic API key cannot be blank. Please try again.
    goto enter_anthropic_key
)

cd /d "%~dp0backend"
(
    echo YOUTUBE_API_KEY=!YOUTUBE_KEY!
    echo ANTHROPIC_API_KEY=!ANTHROPIC_KEY!
) > .env

color 0A
echo.
echo  OK  API keys saved.

:: ----------------------------------------------------------------
:: Done
:: ----------------------------------------------------------------
echo.
color 0A
echo  ============================================================
echo    Setup complete! CommentLens is ready to use.
echo  ============================================================
echo.
echo  To start the app, double-click START.bat
echo.
color 0B
pause
