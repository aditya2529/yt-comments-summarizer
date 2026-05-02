@echo off
setlocal enabledelayedexpansion
color 0E
title CommentLens - Stopping

echo.
echo  ============================================================
echo    CommentLens ^- Stopping Servers
echo  ============================================================
echo.

:: ----------------------------------------------------------------
:: Stop by port (targeted, preferred)
:: ----------------------------------------------------------------
echo  Stopping backend on port 8000...
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8000 " ^| findstr "LISTENING" 2^>nul') do (
    taskkill /PID %%P /F >nul 2>&1
)

echo  Stopping frontend on port 5173...
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":5173 " ^| findstr "LISTENING" 2^>nul') do (
    taskkill /PID %%P /F >nul 2>&1
)

:: ----------------------------------------------------------------
:: Fallback: kill by process name (with warning)
:: ----------------------------------------------------------------
echo.
color 0C
echo  ============================================================
echo    NOTICE
echo  ============================================================
echo.
echo  As a final cleanup, this will also stop ALL Python and
echo  Node.js programs currently running on your computer.
echo.
echo  If you have other unrelated Python or Node.js programs open,
echo  they will also be closed.
echo.
color 0E
echo  Press any key to continue, or close this window to skip.
pause

color 0B
echo.
echo  Stopping all Python processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1

echo  Stopping all Node.js processes...
taskkill /F /IM node.exe >nul 2>&1

:: ----------------------------------------------------------------
:: Done
:: ----------------------------------------------------------------
echo.
color 0A
echo  ============================================================
echo    CommentLens has been stopped.
echo    You can safely close all CommentLens windows.
echo  ============================================================
echo.
color 0B
pause
