"""
Send Test Data to ThingSpeak
Use this to test ThingSpeak write functionality without ESP32
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import requests
import time
from src.config import THINGSPEAK_CHANNEL_ID, THINGSPEAK_READ_API_KEY
from dotenv import load_dotenv
import os

load_dotenv()

WRITE_API_KEY = os.getenv("THINGSPEAK_WRITE_API_KEY", "")

print("=" * 60)
print("  Send Test Data to ThingSpeak")
print("=" * 60)
print()

if not WRITE_API_KEY:
    print("❌ ERROR: THINGSPEAK_WRITE_API_KEY not set in .env file")
    print("\nTo fix:")
    print("1. Edit .env file")
    print("2. Add: THINGSPEAK_WRITE_API_KEY=YOUR_WRITE_KEY")
    print("3. Get Write API Key from ThingSpeak channel > API Keys tab")
    sys.exit(1)

print("Configuration:")
print(f"  Channel ID: {THINGSPEAK_CHANNEL_ID}")
print(f"  Write Key: {'✓ SET' if WRITE_API_KEY else '❌ NOT SET'}")
print()

# Test data
test_readings = [
    {"moisture": 45.2, "ph": 6.5, "temp": 25.3, "humidity": 65.5},
    {"moisture": 46.1, "ph": 6.6, "temp": 25.8, "humidity": 64.2},
    {"moisture": 44.8, "ph": 6.4, "temp": 26.1, "humidity": 63.8},
]

print("Sending test data...")
print()

for i, reading in enumerate(test_readings, 1):
    print(f"[{i}/{len(test_readings)}] Sending:")
    print(f"  Soil Moisture: {reading['moisture']}%")
    print(f"  Soil pH: {reading['ph']}")
    print(f"  Temperature: {reading['temp']}°C")
    print(f"  Humidity: {reading['humidity']}%")
    
    # Build URL
    url = f"https://api.thingspeak.com/update"
    params = {
        "api_key": WRITE_API_KEY,
        "field1": reading['moisture'],
        "field2": reading['ph'],
        "field3": reading['temp'],
        "field4": reading['humidity']
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            entry_id = response.text.strip()
            if entry_id != "0":
                print(f"  ✓ Success! Entry ID: {entry_id}")
            else:
                print(f"  ❌ Failed: ThingSpeak returned 0 (rate limit or error)")
        else:
            print(f"  ❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()
    
    if i < len(test_readings):
        print("  Waiting 20 seconds (ThingSpeak rate limit)...")
        time.sleep(20)

print("=" * 60)
print("Test data sent!")
print()
print("Next steps:")
print("1. Go to your ThingSpeak channel")
print("2. Refresh the page")
print("3. You should see the test data in charts")
print("4. Run: python test_thingspeak.py")
print("5. Run: streamlit run app.py")
print()
