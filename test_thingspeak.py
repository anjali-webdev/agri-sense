"""
Test ThingSpeak Connection
Run this to verify your ThingSpeak configuration
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import THINGSPEAK_CHANNEL_ID, THINGSPEAK_READ_API_KEY
from src.thingspeak_service import ThingSpeakService
import requests

print("=" * 60)
print("  ThingSpeak Connection Test")
print("=" * 60)
print()

# Check configuration
print("1. Checking Configuration...")
print(f"   Channel ID: {THINGSPEAK_CHANNEL_ID if THINGSPEAK_CHANNEL_ID else '❌ NOT SET'}")
print(f"   Read API Key: {'✓ SET' if THINGSPEAK_READ_API_KEY else '❌ NOT SET'}")
print()

if not THINGSPEAK_CHANNEL_ID:
    print("❌ ERROR: THINGSPEAK_CHANNEL_ID not configured")
    print("\nTo fix:")
    print("1. Copy .env.example to .env")
    print("2. Edit .env and add your ThingSpeak credentials")
    print("3. Run this test again")
    sys.exit(1)

# Test internet connection
print("2. Testing Internet Connection...")
try:
    response = requests.get("https://api.thingspeak.com", timeout=5)
    print("   ✓ Can reach ThingSpeak servers")
except Exception as e:
    print(f"   ❌ Cannot reach ThingSpeak: {e}")
    print("\nCheck your internet connection")
    sys.exit(1)

print()

# Test ThingSpeak service
print("3. Testing ThingSpeak Service...")
service = ThingSpeakService()

if not service.is_configured():
    print("   ❌ ThingSpeak service not configured")
    sys.exit(1)

print("   ✓ Service initialized")
print()

# Fetch channel data
print("4. Fetching Channel Data...")
result = service.fetch_channel_feeds(results=10, use_cache=False)

if not result["success"]:
    print(f"   ❌ Failed to fetch data: {result['error']}")
    print("\nPossible issues:")
    print("- Channel ID is incorrect")
    print("- Read API Key is incorrect (if channel is private)")
    print("- Channel has no data yet")
    print("- Rate limit exceeded")
    sys.exit(1)

print("   ✓ Successfully connected to ThingSpeak")
print()

# Parse data
df = service.parse_feeds_to_dataframe(result)

if df is None or df.empty:
    print("5. Channel Status: ⚠️ NO DATA")
    print("\nYour channel is configured correctly but has no data yet.")
    print("\nNext steps:")
    print("1. Upload ESP32 firmware")
    print("2. Configure config.h with WiFi and Write API Key")
    print("3. Upload firmware to ESP32")
    print("4. Wait 1-2 minutes for first reading")
    print("5. Run this test again")
else:
    print("5. Channel Status: ✓ HAS DATA")
    print(f"\n   Records found: {len(df)}")
    print(f"   Latest reading:")
    latest = df.iloc[-1]
    print(f"   - Timestamp: {latest['timestamp']}")
    print(f"   - Soil Moisture: {latest['soil_moisture']:.1f}%")
    print(f"   - Soil pH: {latest['soil_ph']:.2f}")
    print(f"   - Temperature: {latest['temperature']:.1f}°C")
    print(f"   - Humidity: {latest['humidity']:.1f}%")
    print()
    print("✓ ThingSpeak is working correctly!")
    print("\nYou can now run: streamlit run app.py")

print()
print("=" * 60)
