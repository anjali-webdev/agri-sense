@echo off
echo ==========================================
echo   AgriSense AI - Retry Installation
echo ==========================================
echo.

call .venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip --timeout 120
echo.

echo Installing dependencies with extended timeout...
pip install --timeout 120 --default-timeout=120 -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Installation failed. Try these solutions:
    echo 1. Check your internet connection
    echo 2. Run: pip install --no-cache-dir -r requirements.txt
    echo 3. Install packages one by one
    pause
    exit /b 1
)

echo.
echo Installation successful!
echo.
echo Training ML model...
python scripts\train_model.py

echo.
echo ==========================================
echo Ready! Run: streamlit run app.py
echo ==========================================
pause
