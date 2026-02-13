@echo off
chcp 65001 > nul

echo ================================================
echo  Economic YouTube Automation - Install Script
echo ================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed.
    echo Please install Python 3.10+ from: https://python.org
    pause
    exit /b 1
)
echo [1/3] Python OK

REM Upgrade pip with --user flag (for Anaconda)
echo [2/3] Installing packages...
python -m pip install --upgrade pip --user -q
pip install requests beautifulsoup4 feedparser Pillow gtts pydub moviepy --user -q
echo [2/3] Packages installed!

REM Check ffmpeg
echo [3/3] Checking ffmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [REQUIRED] ffmpeg not found!
    echo.
    echo Option 1 - Run this command in cmd (admin):
    echo    winget install ffmpeg
    echo.
    echo Option 2 - Manual install:
    echo    https://ffmpeg.org/download.html
    echo    Extract to C:\ffmpeg
    echo    Add C:\ffmpeg\bin to system PATH
    echo.
) else (
    echo [3/3] ffmpeg OK!
)

echo.
echo ================================================
echo  Done! Now run: run.bat
echo ================================================
pause
