@echo off
echo ==========================================
echo   Quick Install (Latest Versions)
echo ==========================================
echo.

call .venv\Scripts\activate.bat

echo Installing minimal requirements (latest versions)...
pip install --timeout 120 -r requirements_minimal.txt

if %errorlevel% neq 0 (
    echo ERROR: Installation failed
    pause
    exit /b 1
)

echo.
echo Training model...
python scripts\train_model.py

echo.
echo ==========================================
echo Ready! Run: streamlit run app.py
echo ==========================================
pause
