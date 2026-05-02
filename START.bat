@echo off
setlocal enabledelayedexpansion
color 0B
title CommentLens - Starting...

echo.
echo  ============================================================
echo    CommentLens ^- Starting Up
echo  ============================================================
echo.

:: ----------------------------------------------------------------
:: Check setup has been done
:: ----------------------------------------------------------------
if not exist "%~dp0backend\.env" (
    color 0C
    echo  ERROR: Your API keys are not set up yet.
    echo.
    echo  Please double-click SETUP.bat first, then try again.
    echo.
    pause
    exit /b 1
)

:: ----------------------------------------------------------------
:: Check port 8000
:: ----------------------------------------------------------------
echo  Checking port 8000...
netstat -ano | findstr ":8000 " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    color 0E
    echo.
    echo  WARNING: Port 8000 is already in use.
    echo  The backend may already be running.
    echo  If you have problems, run STOP.bat first, then try again.
    echo.
    timeout /t 3 /nobreak >nul
    color 0B
)

:: ----------------------------------------------------------------
:: Check port 5173
:: ----------------------------------------------------------------
echo  Checking port 5173...
netstat -ano | findstr ":5173 " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    color 0E
    echo.
    echo  WARNING: Port 5173 is already in use.
    echo  The frontend may already be running.
    echo  If you have problems, run STOP.bat first, then try again.
    echo.
    timeout /t 3 /nobreak >nul
    color 0B
)

:: ----------------------------------------------------------------
:: Start backend
:: ----------------------------------------------------------------
echo.
echo  Starting backend server...
cd /d "%~dp0backend"
start "CommentLens - Backend" /min cmd /k "color 0A && echo CommentLens Backend is running. Do NOT close this window. && echo. && uvicorn main:app --port 8000"

:: ----------------------------------------------------------------
:: Wait for backend (poll /health every 2s, up to 30s)
:: ----------------------------------------------------------------
echo  Waiting for backend to be ready...
set BACKEND_READY=0
for /l %%i in (1,1,15) do (
    if "!BACKEND_READY!"=="0" (
        timeout /t 2 /nobreak >nul
        curl -s http://localhost:8000/health >nul 2>&1
        if not errorlevel 1 (
            set BACKEND_READY=1
        ) else (
            echo  Still starting... (%%i/15^)
        )
    )
)

if "!BACKEND_READY!"=="0" (
    color 0E
    echo.
    echo  WARNING: Backend is taking longer than usual to start.
    echo  Continuing anyway - the app may need a moment to load.
    echo.
)

color 0A
echo  Backend ready.

:: ----------------------------------------------------------------
:: Start frontend
:: ----------------------------------------------------------------
echo.
color 0B
echo  Starting frontend server...
cd /d "%~dp0frontend"
start "CommentLens - Frontend" /min cmd /k "color 0A && echo CommentLens Frontend is running. Do NOT close this window. && echo. && npm run dev"

:: ----------------------------------------------------------------
:: Wait then open browser
:: ----------------------------------------------------------------
echo  Waiting for frontend to be ready...
timeout /t 5 /nobreak >nul

set FRONTEND_READY=0
for /l %%i in (1,1,10) do (
    if "!FRONTEND_READY!"=="0" (
        curl -s http://localhost:5173 >nul 2>&1
        if not errorlevel 1 (
            set FRONTEND_READY=1
        ) else (
            timeout /t 2 /nobreak >nul
        )
    )
)

echo  Opening CommentLens in your browser...
start "" "http://localhost:5173"

:: ----------------------------------------------------------------
:: Done
:: ----------------------------------------------------------------
echo.
color 0A
echo  ============================================================
echo    CommentLens is running!
echo.
echo    Your browser should open automatically.
echo    If it didn't, go to:  http://localhost:5173
echo.
echo    When you are done using the app, run STOP.bat
echo  ============================================================
echo.
color 0B
echo  You can close this window. The two small windows in your
echo  taskbar (CommentLens - Backend and CommentLens - Frontend)
echo  must stay open while you use the app.
echo.
pause
