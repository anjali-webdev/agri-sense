"""
Interactive .env Configuration Helper
"""
import os
from pathlib import Path

print("=" * 60)
print("  AgriSense AI - Configuration Helper")
print("=" * 60)
print()

# Check if .env already exists
env_file = Path(".env")
if env_file.exists():
    print("⚠️  .env file already exists!")
    response = input("Do you want to overwrite it? (yes/no): ").lower()
    if response != "yes":
        print("Cancelled. Your existing .env file is unchanged.")
        exit(0)

print("Let's configure your ThingSpeak connection.")
print()
print("You have provided:")
print("  Write API Key: XXEPHX4HWZZN8IBV")
print("  Read API Key: SH5CQT9IZ4ILD23P")
print()

# Get Channel ID
channel_id = input("Enter your Channel ID (the number at top of ThingSpeak page): ").strip()

if not channel_id or not channel_id.isdigit():
    print("❌ Invalid Channel ID. Please enter numbers only.")
    exit(1)

print()
print("Creating .env file with your configuration...")

# Create .env content
env_content = f"""# ThingSpeak Configuration
THINGSPEAK_CHANNEL_ID={channel_id}
THINGSPEAK_READ_API_KEY=SH5CQT9IZ4ILD23P
THINGSPEAK_WRITE_API_KEY=XXEPHX4HWZZN8IBV

# Device Configuration
DEVICE_ID=ESP32_AGRISENSE_01

# Application Settings
DATA_FRESHNESS_MINUTES=30
CHART_REFRESH_INTERVAL_SECONDS=300
ENABLE_DEMO_MODE=false

# Alert Thresholds (Optional - can be configured in UI)
ALERT_SOIL_MOISTURE_MIN=20
ALERT_SOIL_MOISTURE_MAX=80
ALERT_SOIL_PH_MIN=5.5
ALERT_SOIL_PH_MAX=8.0
ALERT_TEMPERATURE_MIN=10
ALERT_TEMPERATURE_MAX=45
ALERT_HUMIDITY_MIN=30
ALERT_HUMIDITY_MAX=90
"""

# Write .env file
with open(".env", "w") as f:
    f.write(env_content)

print("✓ .env file created successfully!")
print()
print("Configuration Summary:")
print(f"  Channel ID: {channel_id}")
print(f"  Read API Key: SH5CQT9IZ4ILD23P")
print(f"  Write API Key: XXEPHX4HWZZN8IBV")
print(f"  Demo Mode: DISABLED (will use live ThingSpeak data)")
print()
print("=" * 60)
print("Next Steps:")
print("=" * 60)
print()
print("1. Test ThingSpeak connection:")
print("   python test_thingspeak.py")
print()
print("2. Send test data (optional, to verify channel works):")
print("   python send_test_data.py")
print()
print("3. Run the application:")
print("   streamlit run app.py")
print()
print("4. Configure ESP32 firmware (see ESP32_SETUP.txt)")
print()
