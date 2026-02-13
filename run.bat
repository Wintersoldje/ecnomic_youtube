@echo off
chcp 65001 > nul
echo ================================================
echo  Economic YouTube Automation - START
echo ================================================
echo.
cd /d "%~dp0"
python main.py
echo.
echo Output files saved in: output folder
echo   - output\shorts_video.mp4   (YouTube Shorts)
echo   - output\longform_video.mp4 (YouTube Long-form)
echo.
pause
