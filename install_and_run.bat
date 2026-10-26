@echo off
echo ==========================================
echo   AgriSense AI - Installation and Setup
echo ==========================================
echo.

echo [1/4] Creating virtual environment...
python -m venv .venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    echo Make sure Python 3.8+ is installed
    pause
    exit /b 1
)
echo Done.
echo.

echo [2/4] Installing dependencies...
call .venv\Scripts\activate.bat
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Done.
echo.

echo [3/4] Training ML model...
python scripts\train_model.py
if %errorlevel% neq 0 (
    echo WARNING: Model training failed
    echo You can try again later with: python scripts\train_model.py
)
echo Done.
echo.

echo [4/4] Starting application...
echo.
echo ==========================================
echo   AgriSense AI will open in your browser
echo   URL: http://localhost:8501
echo ==========================================
echo.
streamlit run app.py
