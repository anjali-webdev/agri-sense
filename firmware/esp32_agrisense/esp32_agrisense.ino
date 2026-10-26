/*
 * AgriSense AI - ESP32 Firmware
 * Smart Agriculture IoT Sensor Node
 * 
 * Reads soil moisture, pH, temperature, and humidity sensors
 * Uploads data to ThingSpeak IoT platform via Wi-Fi
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"
#include "config.h"

// DHT Sensor Configuration
#define DHTPIN 4          // DHT22 data pin
#define DHTTYPE DHT22     // DHT22 sensor type
DHT dht(DHTPIN, DHTTYPE);

// Sensor Pin Configuration
#define SOIL_MOISTURE_PIN 34  // Analog pin for soil moisture
#define SOIL_PH_PIN 35        // Analog pin for soil pH (requires signal conditioning)

// Calibration values for soil moisture
#define MOISTURE_MIN 0        // ADC value for completely dry soil
#define MOISTURE_MAX 4095     // ADC value for completely wet soil

// Calibration values for pH sensor (adjust based on your sensor)
#define PH_VOLTAGE_7 2.5      // Voltage at pH 7
#define PH_VOLTAGE_4 3.0      // Voltage at pH 4

// ThingSpeak Configuration
const char* server = "api.thingspeak.com";
const int uploadInterval = 60000;  // Upload every 60 seconds (minimum 15 seconds)

// Enable test mode (no real sensors needed)
#define TEST_MODE false  // Set to true to send test data without sensors

// Variables
unsigned long lastUploadTime = 0;
float temperature = 0;
float humidity = 0;
float soilMoisture = 0;
float soilPH = 0;

void setup() {
  // Initialize Serial Monitor
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n===========================================");
  Serial.println("  AgriSense AI - ESP32 Sensor Node");
  Serial.println("===========================================\n");
  
  // Initialize DHT sensor
  dht.begin();
  Serial.println("✓ DHT22 sensor initialized");
  
  // Initialize analog pins
  pinMode(SOIL_MOISTURE_PIN, INPUT);
  pinMode(SOIL_PH_PIN, INPUT);
  Serial.println("✓ Analog pins configured");
  
  // Connect to Wi-Fi
  connectWiFi();
  
  Serial.println("\n✓ Setup complete!");
  Serial.println("Starting sensor readings...\n");
}

void loop() {
  // Check Wi-Fi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠ Wi-Fi disconnected. Reconnecting...");
    connectWiFi();
  }
  
  // Check if it's time to upload
  unsigned long currentTime = millis();
  
  if (currentTime - lastUploadTime >= uploadInterval) {
    // Read all sensors
    readSensors();
    
    // Display readings
    displayReadings();
    
    // Upload to ThingSpeak
    uploadToThingSpeak();
    
    lastUploadTime = currentTime;
  }
  
  delay(1000);  // Small delay between loops
}

void connectWiFi() {
  Serial.print("Connecting to Wi-Fi: ");
  Serial.println(WIFI_SSID);
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ Connected to Wi-Fi");
    Serial.print("  IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n✗ Failed to connect to Wi-Fi");
    Serial.println("  Check SSID and password in config.h");
  }
}

void readSensors() {
  #if TEST_MODE
  // Test mode - generate random but realistic sensor data
  temperature = 20.0 + (float)(random(0, 100)) / 10.0;  // 20-30°C
  humidity = 50.0 + (float)(random(0, 300)) / 10.0;     // 50-80%
  soilMoisture = 30.0 + (float)(random(0, 400)) / 10.0; // 30-70%
  soilPH = 6.0 + (float)(random(0, 20)) / 10.0;         // 6.0-8.0
  Serial.println("⚠ TEST MODE: Using simulated sensor data");
  return;
  #endif
  
  // Read DHT22 sensor
  humidity = dht.readHumidity();
  temperature = dht.readTemperature();
  
  // Check if DHT reading failed
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("⚠ Failed to read from DHT sensor!");
    humidity = 0;
    temperature = 0;
  }
  
  // Read soil moisture sensor
  int moistureRaw = analogRead(SOIL_MOISTURE_PIN);
  soilMoisture = map(moistureRaw, MOISTURE_MIN, MOISTURE_MAX, 0, 100);
  soilMoisture = constrain(soilMoisture, 0, 100);
  
  // Read soil pH sensor (requires proper signal conditioning and calibration)
  int phRaw = analogRead(SOIL_PH_PIN);
  float phVoltage = (phRaw / 4095.0) * 3.3;  // Convert ADC to voltage
  soilPH = calculatePH(phVoltage);
  soilPH = constrain(soilPH, 0, 14);
}

float calculatePH(float voltage) {
  // Linear pH calculation (adjust based on your sensor calibration)
  // This is a simplified calculation - proper pH sensors require multi-point calibration
  float slope = (7.0 - 4.0) / (PH_VOLTAGE_7 - PH_VOLTAGE_4);
  float ph = 7.0 - slope * (voltage - PH_VOLTAGE_7);
  return ph;
}

void displayReadings() {
  Serial.println("--- Sensor Readings ---");
  Serial.print("  Temperature:    ");
  Serial.print(temperature, 1);
  Serial.println(" °C");
  
  Serial.print("  Humidity:       ");
  Serial.print(humidity, 1);
  Serial.println(" %");
  
  Serial.print("  Soil Moisture:  ");
  Serial.print(soilMoisture, 1);
  Serial.println(" %");
  
  Serial.print("  Soil pH:        ");
  Serial.println(soilPH, 2);
  Serial.println();
}

void uploadToThingSpeak() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("✗ Cannot upload - No Wi-Fi connection");
    return;
  }
  
  // Validate readings before uploading
  if (!validateReadings()) {
    Serial.println("⚠ Skipping upload - Invalid sensor readings");
    return;
  }
  
  HTTPClient http;
  
  // Build ThingSpeak URL
  String url = "http://";
  url += server;
  url += "/update?api_key=";
  url += THINGSPEAK_WRITE_API_KEY;
  url += "&field1=";
  url += String(soilMoisture, 1);
  url += "&field2=";
  url += String(soilPH, 2);
  url += "&field3=";
  url += String(temperature, 1);
  url += "&field4=";
  url += String(humidity, 1);
  
  Serial.print("Uploading to ThingSpeak... ");
  
  http.begin(url);
  int httpCode = http.GET();
  
  if (httpCode > 0) {
    String payload = http.getString();
    if (httpCode == 200 && payload.toInt() > 0) {
      Serial.println("✓ Upload successful");
    } else {
      Serial.print("⚠ Upload failed. HTTP code: ");
      Serial.println(httpCode);
    }
  } else {
    Serial.print("✗ Upload error: ");
    Serial.println(http.errorToString(httpCode).c_str());
  }
  
  http.end();
}

bool validateReadings() {
  // Check for NaN values
  if (isnan(temperature) || isnan(humidity) || isnan(soilMoisture) || isnan(soilPH)) {
    return false;
  }
  
  // Check physical ranges
  if (temperature < -40 || temperature > 85) return false;
  if (humidity < 0 || humidity > 100) return false;
  if (soilMoisture < 0 || soilMoisture > 100) return false;
  if (soilPH < 0 || soilPH > 14) return false;
  
  return true;
}
