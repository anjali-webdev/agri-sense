/*
 * AgriSense AI - Configuration File
 * 
 * INSTRUCTIONS:
 * 1. Enter your WiFi network name and password
 * 2. ThingSpeak credentials are already configured
 * 3. Save this file
 * 4. Upload to ESP32
 */

#ifndef CONFIG_H
#define CONFIG_H

// ========== WiFi Configuration ==========
// ⚠️ CHANGE THESE TO YOUR WiFi CREDENTIALS ⚠️
#define WIFI_SSID "YOUR_WIFI_NETWORK_NAME"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// ========== ThingSpeak Configuration ==========
// Already configured for your channel
#define THINGSPEAK_CHANNEL_ID "3549032"
#define THINGSPEAK_WRITE_API_KEY "XXEPHX4HWZZN8IBV"

// ========== Device Configuration ==========
#define DEVICE_NAME "AgriSense_ESP32"
#define FIRMWARE_VERSION "1.0.0"

#endif
