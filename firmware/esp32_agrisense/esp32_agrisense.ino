/*
 * AgriSense AI - ESP32 IoT Sensor Node
 * 
 * Reads soil moisture, pH, temperature, and humidity sensors
 * Sends data to ThingSpeak cloud platform every 60 seconds
 * 
 * Hardware:
 * - ESP32 DevKit
 * - DHT11 Temperature & Humidity Sensor (GPIO 4)
 * - Soil Moisture Sensor (GPIO 34)
 * - pH Sensor EBC201-C with probe (GPIO 35)
 * 
 * Created for AgriSense AI Crop Recommendation System
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include "config.h"

// ---------- PIN CONFIGURATION ----------
#define DHT_PIN 4
#define DHT_TYPE DHT11
#define SOIL_PIN 34
#define PH_PIN 35

DHT dht(DHT_PIN, DHT_TYPE);

// ---------- TIMING CONFIGURATION ----------
unsigned long lastUpdate = 0;
const unsigned long UPDATE_INTERVAL = 60000; // Send data every 60 seconds

// ---------- SOIL MOISTURE CALIBRATION ----------
// Adjust these values after testing your sensor in dry and wet soil
const int SOIL_DRY = 4095;  // ADC reading in completely dry soil
const int SOIL_WET = 1500;  // ADC reading in saturated soil

// ---------- pH SENSOR CALIBRATION ----------
// For EBC201-C pH sensor
const float PH_VOLTAGE_AT_PH7 = 2.50;  // Voltage at pH 7.0 (calibrate with buffer)
const float PH_SLOPE = 0.18;           // Volts per pH unit (calibrate with buffers)

// ---------- SYSTEM STATUS ----------
int readingCount = 0;
bool wifiConnected = false;

void setup() {
  Serial.begin(9600);
  delay(1000);
  
  // Configure ADC
  analogReadResolution(12);  // 12-bit resolution (0-4095)
  analogSetPinAttenuation(SOIL_PIN, ADC_11db);  // Full 0-3.3V range
  analogSetPinAttenuation(PH_PIN, ADC_11db);
  
  // Initialize DHT sensor
  dht.begin();
  
  // Display startup banner
  Serial.println();
  Serial.println("====================================");
  Serial.println("   AGRISENSE AI - ESP32 IoT NODE");
  Serial.println("====================================");
  Serial.println("Hardware: DHT11 + Soil + pH Sensor");
  Serial.println("Platform: ThingSpeak IoT Cloud");
  Serial.println("====================================");
  Serial.println();
  
  // Connect to WiFi
  connectWiFi();
  
  Serial.println();
  Serial.println("System Ready!");
  Serial.println("Sending data every 60 seconds...");
  Serial.println("====================================");
  
  delay(2000);
}

void loop() {
  unsigned long currentTime = millis();
  
  // Send data at regular intervals
  if (currentTime - lastUpdate >= UPDATE_INTERVAL) {
    readAndSendData();
    lastUpdate = currentTime;
  }
  
  // Check WiFi connection periodically
  if (WiFi.status() != WL_CONNECTED && wifiConnected) {
    Serial.println("\n[WARNING] WiFi disconnected! Reconnecting...");
    wifiConnected = false;
    connectWiFi();
  }
  
  delay(100);
}

void connectWiFi() {
  Serial.println();
  Serial.println("Connecting to WiFi...");
  Serial.print("SSID: ");
  Serial.println(WIFI_SSID);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  Serial.println();
  
  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    Serial.println("✓ WiFi Connected Successfully!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal Strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    wifiConnected = false;
    Serial.println("✗ WiFi Connection Failed!");
    Serial.println("Check your SSID and password in config.h");
  }
}

void readAndSendData() {
  readingCount++;
  
  Serial.println();
  Serial.println("========================================");
  Serial.print("READING #");
  Serial.println(readingCount);
  Serial.println("========================================");
  
  // ---------- READ DHT11 SENSOR ----------
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  
  Serial.println();
  Serial.println("[DHT11 - Temperature & Humidity]");
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("✗ DHT11 read failed - check wiring!");
    Serial.println("  Temperature: ERROR");
    Serial.println("  Humidity: ERROR");
  } else {
    Serial.print("  Temperature: ");
    Serial.print(temperature, 1);
    Serial.println(" °C");
    Serial.print("  Humidity: ");
    Serial.print(humidity, 1);
    Serial.println(" %");
  }
  
  // ---------- READ SOIL MOISTURE SENSOR ----------
  long soilTotal = 0;
  for (int i = 0; i < 10; i++) {
    soilTotal += analogRead(SOIL_PIN);
    delay(10);
  }
  int soilRaw = soilTotal / 10;
  
  // Map to percentage (0-100%)
  int soilMoisture = map(soilRaw, SOIL_DRY, SOIL_WET, 0, 100);
  soilMoisture = constrain(soilMoisture, 0, 100);
  
  Serial.println();
  Serial.println("[SOIL MOISTURE SENSOR]");
  Serial.print("  Raw ADC: ");
  Serial.println(soilRaw);
  
  if (soilRaw >= 4090 || soilRaw <= 5) {
    Serial.println("  ⚠ Warning: Sensor may be disconnected!");
  }
  
  Serial.print("  Soil Moisture: ");
  Serial.print(soilMoisture);
  Serial.println(" %");
  
  // ---------- READ pH SENSOR (EBC201-C) ----------
  long phTotal = 0;
  for (int i = 0; i < 10; i++) {
    phTotal += analogRead(PH_PIN);
    delay(10);
  }
  int phRaw = phTotal / 10;
  
  // Calculate voltage and pH
  float gpioVoltage = analogReadMilliVolts(PH_PIN) / 1000.0;
  float boardVoltage = gpioVoltage * 2.0;  // Voltage divider compensation
  float pH = 7.0 + (PH_VOLTAGE_AT_PH7 - boardVoltage) / PH_SLOPE;
  pH = constrain(pH, 0.0, 14.0);
  
  Serial.println();
  Serial.println("[pH SENSOR - EBC201-C]");
  Serial.print("  Raw ADC: ");
  Serial.println(phRaw);
  Serial.print("  GPIO Voltage: ");
  Serial.print(gpioVoltage, 3);
  Serial.println(" V");
  Serial.print("  Board Voltage: ");
  Serial.print(boardVoltage, 3);
  Serial.println(" V");
  Serial.print("  Soil pH: ");
  Serial.println(pH, 2);
  
  Serial.println();
  Serial.println("========================================");
  
  // ---------- VALIDATE READINGS ----------
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("✗ Cannot send - DHT11 reading failed!");
    Serial.println("========================================");
    return;
  }
  
  // ---------- SEND TO THINGSPEAK ----------
  if (WiFi.status() == WL_CONNECTED) {
    sendToThingSpeak(soilMoisture, pH, temperature, humidity);
  } else {
    Serial.println("✗ Cannot send - WiFi not connected!");
    Serial.println("========================================");
  }
}

void sendToThingSpeak(float moisture, float pH, float temp, float humidity) {
  Serial.println();
  Serial.println("Uploading to ThingSpeak IoT Cloud...");
  
  HTTPClient http;
  
  // Build ThingSpeak update URL
  String url = String("http://api.thingspeak.com/update?api_key=") + 
               THINGSPEAK_WRITE_API_KEY +
               "&field1=" + String(moisture, 1) +
               "&field2=" + String(pH, 2) +
               "&field3=" + String(temp, 1) +
               "&field4=" + String(humidity, 1);
  
  Serial.println("  Field 1 (Soil Moisture): " + String(moisture, 1) + " %");
  Serial.println("  Field 2 (Soil pH): " + String(pH, 2));
  Serial.println("  Field 3 (Temperature): " + String(temp, 1) + " °C");
  Serial.println("  Field 4 (Humidity): " + String(humidity, 1) + " %");
  
  http.begin(url);
  http.setTimeout(10000);  // 10 second timeout
  
  int httpCode = http.GET();
  
  if (httpCode > 0) {
    String response = http.getString();
    int entryId = response.toInt();
    
    if (entryId > 0) {
      Serial.println();
      Serial.println("✓ SUCCESS! Data uploaded to ThingSpeak");
      Serial.print("  Entry ID: ");
      Serial.println(entryId);
      Serial.print("  Channel: ");
      Serial.println(THINGSPEAK_CHANNEL_ID);
    } else {
      Serial.println();
      Serial.println("✗ FAILED! ThingSpeak returned error");
      Serial.println("  Possible causes:");
      Serial.println("  - Rate limit (wait 15-20 seconds between updates)");
      Serial.println("  - Invalid Write API Key");
      Serial.println("  - Channel not found");
    }
  } else {
    Serial.println();
    Serial.println("✗ HTTP Request Failed!");
    Serial.print("  Error code: ");
    Serial.println(httpCode);
  }
  
  http.end();
  Serial.println("========================================");
}
