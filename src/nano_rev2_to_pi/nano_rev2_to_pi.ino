/*
Author: Jason Huang
Date: 27-May-23 
Rev: 01
 
Purpose: Utilize Arduino Nano 33 BLE Sense Rev 2 with it's integrated BLE and on-board sensors, to send acquired data to Raspberry Pi 3/4
 
Adapted by: Fernando Kendy M. Arake
Date: April-24

*/
 
#include "Arduino_BMI270_BMM150.h"
#include <ArduinoBLE.h>
#include <Arduino_HS300x.h>
#include <Arduino_LPS22HB.h>

unsigned int previousHumidity = 0;
unsigned int previousTemperature = 0;
unsigned int previousPressure = 0;
 

int x, y, z;
int degreesX = 0;
int degreesY = 0;
float previousdegreesX = 0.0;
float previousdegreesY = 0.0;


union imu_sensor_data {
  struct __attribute__((packed)) {
    float values[3]; // float array for data (it holds 3)
    bool updated = false;
  };
  uint8_t bytes[3 * sizeof(float)]; // size as byte array 
};

union imu_sensor_data accData;
union imu_sensor_data gyroData;
union imu_sensor_data magData;
 
// Define the UUID for the service and characteristics
#define SERVICE_UUID        "12345678-1234-5678-1234-56789abcdef0"
 
// Create a BLE service and characteristic
BLEService bleService(SERVICE_UUID);
 
// To find the specifics UUID: https://btprodspecificationrefs.blob.core.windows.net/assigned-numbers/Assigned%20Number%20Types/Assigned_Numbers.pdf#page=71
// Apparently these are specific for official BLE stuff, so better use a randomly generated one: 

BLEIntCharacteristic tempCharacteristic("7e45d293-9b2a-4812-899a-b3a111fa0f67", BLERead | BLENotify); // Standard 16-bit Temperature characteristic
BLEUnsignedIntCharacteristic humidCharacteristic("33e6cf6f-f1f3-44c5-8dd5-bb0cb2d9e2f8", BLERead | BLENotify); // Unsigned 16-bit Humidity characteristic
BLEIntCharacteristic pressureCharacteristic("f327aae5-349f-4c7f-a812-e60c7cfc5968", BLERead | BLENotify);
BLECharacteristic accelerometerCharacteristic("12345678-1234-5678-1234-56789abcdef1", BLERead | BLENotify, sizeof accData.bytes); // Standard 16-bit characteristic
BLECharacteristic gyroCharacteristic("d43306de-76e7-4b06-971c-9d8cc499290e", BLERead | BLENotify, sizeof gyroData.bytes); // Standard 16-bit characteristic
BLECharacteristic magCharacteristic("4bdf3152-ffe6-4d6f-8a28-c43a5e8c1bc2", BLERead | BLENotify, sizeof magData.bytes); // Standard 16-bit characteristic

  


void setup() {
   
  Serial.begin(9600);
  while (!Serial);
  Serial.println("Started");
 
 
  if (!HS300x.begin()) {
 
    Serial.println("Failed to initialize humidity temperature sensor!");
    while (1);
 
  }
   
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }
 
  if (!BARO.begin()) {
    Serial.println("Failed to initialize pressure sensor!");
    while (1);
  }

  Serial.print("Accelerometer sample rate = ");
  Serial.print(IMU.accelerationSampleRate());
  Serial.println(" Hz");
   
  pinMode(LED_BUILTIN, OUTPUT); // Initialize the built-in LED pin
   
  if (!BLE.begin()) { // Initialize NINA B306 BLE
      Serial.println("starting BLE failed!");
      while (1);
  }
  
  BLE.setLocalName("JH_ArduinoNano33BLESense_R2");    // Set name for connection
  BLE.setAdvertisedService(bleService); // Advertise ble service
  
  bleService.addCharacteristic(tempCharacteristic);     // Add temperature characteristic
  bleService.addCharacteristic(humidCharacteristic);    // Add humidity characteristic
  bleService.addCharacteristic(pressureCharacteristic); 
  bleService.addCharacteristic(accelerometerCharacteristic);
  bleService.addCharacteristic(gyroCharacteristic);
  bleService.addCharacteristic(magCharacteristic);
  BLE.addService(bleService); // Add environment service
   
  tempCharacteristic.setValue(0);     // Set initial temperature value
  humidCharacteristic.setValue(0);    // Set initial humidity value
  pressureCharacteristic.setValue(0);

  for (int i = 0; i < 3; i++) {
    accData.values[i] = i;
    gyroData.values[i] = i;
    magData.values[i] = i;
  }

     
  BLE.advertise(); // Start advertising
  Serial.print("Peripheral device MAC: ");
  Serial.println(BLE.address());
  Serial.println("Waiting for connections…");
}
 
void loop() {
   
  BLEDevice central = BLE.central(); // Wait for a BLE central to connect
 
 
  // If central is connected to peripheral
  if (central) {
      Serial.print("Connected to central MAC: ");
      Serial.println(central.address()); // Central's BT address:
 
      digitalWrite(LED_BUILTIN, HIGH); // Turn on the LED to indicate the connection
 
      while (central.connected()) {
        updateReadings();
        accSensorTask();
        gyroSensorTask();
        magSensorTask();
        delay(100);
      }
 
      digitalWrite(LED_BUILTIN, LOW); // When the central disconnects, turn off the LED
      Serial.print("Disconnected from central MAC: ");
      Serial.println(central.address());
  }
}
 
bool accSensorTask() {
  static float x = 0.00, y = 0.00, z = 0.00;
  if(IMU.accelerationAvailable()){
    IMU.readAcceleration(x, y, z);
    accData.values[0] = x; // 0.11
    accData.values[1] = y; // 1.13
    accData.values[2] = z; // -1.13
    accData.updated = true;
  }
  return accData.updated;
}

bool gyroSensorTask() {
  static float x = 0.00, y = 0.00, z = 0.00;
  if(IMU.gyroscopeAvailable()){
    IMU.readGyroscope(x, y, z);
    gyroData.values[0] = x; // 0.11
    gyroData.values[1] = y; // 1.13
    gyroData.values[2] = z; // -1.13
    gyroData.updated = true;
  }
  return gyroData.updated;
}

bool magSensorTask() {
  static float x = 0.00, y = 0.00, z = 0.00;
  if(IMU.magneticFieldAvailable()){
    IMU.readMagneticField(x, y, z);
    magData.values[0] = x; // 0.11
    magData.values[1] = y; // 1.13
    magData.values[2] = z; // -1.13
    magData.updated = true;
  }
  return magData.updated;
}
 
unsigned int getHumidity() {
    // Get humidity as unsigned 16-bit int for BLE characteristic
    return (unsigned int) (HS300x.readHumidity()*100);
}
 
unsigned int getTemperature() {
    // Get humidity as unsigned 16-bit int for BLE characteristic
    return (unsigned int) (HS300x.readTemperature()*100);
}
 
unsigned int getPressure(){
  return (unsigned int) (BARO.readPressure()*100);
}
 
void updateReadings() {
 
    unsigned int humidity = getHumidity();
    unsigned int temperature = getTemperature();
    unsigned int pressure = getPressure();
      
 
    if (temperature != previousTemperature) { // If reading has changed
        Serial.print("Temperature: ");
        Serial.println(temperature);
        tempCharacteristic.writeValue(temperature); // Update characteristic
        previousTemperature = temperature;          // Save value
    }
 
    if (humidity != previousHumidity) { // If reading has changed
        Serial.print("Humidity: ");
        Serial.println(humidity);
        humidCharacteristic.writeValue(humidity);
        previousHumidity = humidity;
    }
 
    if (pressure != previousPressure) { // comes in kPa
      Serial.print("Pressure: ");
      Serial.println(pressure);
      pressureCharacteristic.writeValue(pressure);
      previousPressure = pressure;
    }

    if (accData.updated) {
      int16_t accelerometer_X = round(accData.values[0] * 100.0);
      int16_t accelerometer_Y = round(accData.values[1] * 100.0);
      int16_t accelerometer_Z = round(accData.values[2] * 100.0);
      Serial.print("X: ");
      Serial.println(accelerometer_X);
      Serial.print("Y: ");
      Serial.println(accelerometer_Y);
      Serial.print("Z: ");
      Serial.println(accelerometer_Z);
      accelerometerCharacteristic.writeValue(accData.bytes, sizeof accData.bytes);
      accData.updated = false;
    }
    
    if (gyroData.updated) {
      // int16_t gyro_X = round(gyroData.values[0] * 100.0);
      // int16_t gyro_Y = round(gyroData.values[1] * 100.0);
      // int16_t gyro_Z = round(gyroData.values[2] * 100.0);
      gyroCharacteristic.writeValue(gyroData.bytes, sizeof gyroData.bytes);
      gyroData.updated = false;
    }

    if (magData.updated) {
      // int16_t mag_X = round(magData.values[0] * 100.0);
      // int16_t mag_Y = round(magData.values[1] * 100.0);
      // int16_t mag_Z = round(magData.values[2] * 100.0);
      magCharacteristic.writeValue(magData.bytes, sizeof magData.bytes);
      magData.updated = false;
    }
}