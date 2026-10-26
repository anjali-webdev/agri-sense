@echo off
echo ==========================================
echo   Fixing NumPy Version Conflict
echo ==========================================
echo.

call .venv\Scripts\activate.bat

echo Upgrading NumPy to version 2.0+...
pip install --upgrade "numpy>=2.0.0"

if %errorlevel% neq 0 (
    echo ERROR: Failed to upgrade NumPy
    pause
    exit /b 1
)

echo.
echo NumPy upgraded successfully!
echo.
echo Testing application...
python -c "import numpy; print(f'NumPy version: {numpy.__version__}')"
python -c "import streamlit; print('Streamlit OK')"
echo.
echo ==========================================
echo Fixed! Now run: streamlit run app.py
echo ==========================================
pause
