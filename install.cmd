@echo off
REM Gagiteck Assets Installation Script for Windows
REM This script sets up the Gagiteck robots.txt repository

setlocal enabledelayedexpansion

REM Configuration
set REPO_NAME=gagiteck-assets
set REPO_URL=https://github.com/ajaniethos-1/gagiteck-assets.git
set INSTALL_DIR=%USERPROFILE%\%REPO_NAME%

echo ============================================================
echo   Gagiteck Assets - robots.txt Deployment Setup
echo ============================================================
echo.

REM Check prerequisites
echo Checking prerequisites...
echo.

REM Check for Git
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [X] Git is not installed.
    echo     Please install Git from: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)
echo [OK] Git is installed

REM Check for curl
where curl >nul 2>nul
if %errorlevel% neq 0 (
    echo [X] curl is not installed.
    echo     Please install curl or use Windows 10/11 which includes it.
    echo.
    pause
    exit /b 1
)
echo [OK] curl is installed

echo.

REM Clone or update repository
if exist "%INSTALL_DIR%" (
    echo Repository already exists at %INSTALL_DIR%
    echo Updating repository...
    cd /d "%INSTALL_DIR%"
    git fetch origin
    git pull origin main
    if %errorlevel% neq 0 (
        echo [X] Failed to update repository
        pause
        exit /b 1
    )
    echo [OK] Repository updated
) else (
    echo Cloning repository to %INSTALL_DIR%...
    git clone "%REPO_URL%" "%INSTALL_DIR%"
    if %errorlevel% neq 0 (
        echo [X] Failed to clone repository
        pause
        exit /b 1
    )
    cd /d "%INSTALL_DIR%"
    echo [OK] Repository cloned
)

echo.

REM Display setup instructions
echo ============================================================
echo   Setup Complete!
echo ============================================================
echo.
echo Repository installed at: %INSTALL_DIR%
echo.
echo NEXT STEPS:
echo.
echo 1. ENABLE GITHUB PAGES:
echo    - Go to: https://github.com/ajaniethos-1/gagiteck-assets/settings/pages
echo    - Set source to 'main' branch and '/' (root) folder
echo    - Save the settings
echo.
echo 2. VERIFY DEPLOYMENT:
echo    - Wait a few minutes for GitHub Pages to deploy
echo    - Visit: https://ajaniethos-1.github.io/gagiteck-assets/robots.txt
echo.
echo 3. SETUP CLOUDFLARE WORKER (Optional):
echo    - Log in to Cloudflare Dashboard
echo    - Create a new Worker
echo    - Copy the worker script from README.md
echo    - Add route: www.gagiteck.com/robots.txt
echo.
echo 4. VERIFY FINAL SETUP:
echo    - Test: https://www.gagiteck.com/robots.txt
echo    - Use Google Search Console to verify accessibility
echo.
echo Installation complete! Check README.md for detailed instructions.
echo.
pause
