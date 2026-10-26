@echo off
echo ==========================================
echo   Installing packages individually
echo ==========================================
echo.

call .venv\Scripts\activate.bat

echo [1/9] Installing streamlit...
pip install streamlit==1.31.0 --timeout 120

echo [2/9] Installing pandas...
pip install pandas==2.2.0 --timeout 120

echo [3/9] Installing numpy...
pip install numpy==1.26.3 --timeout 120

echo [4/9] Installing scikit-learn...
pip install scikit-learn==1.4.0 --timeout 120

echo [5/9] Installing joblib...
pip install joblib==1.3.2 --timeout 120

echo [6/9] Installing plotly...
pip install plotly==5.18.0 --timeout 120

echo [7/9] Installing requests...
pip install requests==2.31.0 --timeout 120

echo [8/9] Installing python-dotenv...
pip install python-dotenv==1.0.1 --timeout 120

echo [9/9] Installing pytest...
pip install pytest==8.0.0 pytest-mock==3.12.0 --timeout 120

echo.
echo ==========================================
echo Installation complete!
echo ==========================================
echo.
echo Training model...
python scripts\train_model.py

echo.
echo Ready! Run: streamlit run app.py
pause
