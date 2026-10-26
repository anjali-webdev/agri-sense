@echo off
echo ==========================================
echo   Testing Your ThingSpeak Channel
echo ==========================================
echo.
echo Channel ID: 3549032
echo Read API Key: SH5CQT9IZ4ILD23P
echo Write API Key: XXEPHX4HWZZN8IBV
echo.

call .venv\Scripts\activate.bat

echo Step 1: Testing connection...
python test_thingspeak.py
echo.
echo.

echo Step 2: Send test data? (Y/N)
set /p answer=
if /i "%answer%"=="Y" (
    echo Sending test data to your channel...
    python send_test_data.py
    echo.
    echo Go to: https://thingspeak.com/channels/3549032
    echo Refresh the page to see your data!
)

echo.
echo ==========================================
echo Ready to run application!
echo ==========================================
echo.
echo Run: streamlit run app.py
pause
