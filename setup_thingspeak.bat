@echo off
echo ==========================================
echo   AgriSense AI - ThingSpeak Setup
echo ==========================================
echo.
echo Your API Keys:
echo   Write Key: XXEPHX4HWZZN8IBV
echo   Read Key:  SH5CQT9IZ4ILD23P
echo.

call .venv\Scripts\activate.bat

python configure_env.py

pause
