#include <Adafruit_Fingerprint.h>
#include <Wire.h>
#include <Adafruit_MLX90614.h>
#include "MAX30105.h"
#include "heartRate.h"
#include <ArduinoJson.h>

const int RED_LED = 11;
const int YELLOW_LED = 12;
const int GREEN_LED = 13;

HardwareSerial mySerial(1);
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);

Adafruit_MLX90614 mlx = Adafruit_MLX90614();
MAX30105 particleSensor;

bool sessionActive = false;

void setup() {
  Serial.begin(115200);
  while (!Serial);

  pinMode(RED_LED, OUTPUT);
  pinMode(YELLOW_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);

  // R503 Setup
  finger.begin(57600);
  if (finger.verifyPassword()) {
    finger.LEDcontrol(FINGERPRINT_LED_BREATHING, 100, FINGERPRINT_LED_BLUE);
  } else {
    while (1) {
      digitalWrite(RED_LED, HIGH);
      delay(500);
      digitalWrite(RED_LED, LOW);
      delay(500);
    }
  }

  // MLX90614 Setup
  mlx.begin();

  // MAX30102 Setup
  if (particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    particleSensor.setup();
    particleSensor.setPulseAmplitudeRed(0x0A);
    particleSensor.setPulseAmplitudeGreen(0);
  }
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    handleCommand(cmd);
  }

  if (!sessionActive) {
    checkFingerprint();
  }
}

void handleCommand(String cmd) {
  if (cmd == "START_SENSORS") {
    readSensorsAndSend();
  } else if (cmd == "LIGHT_RED") {
    digitalWrite(RED_LED, HIGH);
    digitalWrite(YELLOW_LED, LOW);
    digitalWrite(GREEN_LED, LOW);
  } else if (cmd == "LIGHT_YELLOW") {
    digitalWrite(RED_LED, LOW);
    digitalWrite(YELLOW_LED, HIGH);
    digitalWrite(GREEN_LED, LOW);
  } else if (cmd == "LIGHT_GREEN") {
    digitalWrite(RED_LED, LOW);
    digitalWrite(YELLOW_LED, LOW);
    digitalWrite(GREEN_LED, HIGH);
  } else if (cmd == "RESET_SESSION") {
    sessionActive = false;
    digitalWrite(RED_LED, LOW);
    digitalWrite(YELLOW_LED, LOW);
    digitalWrite(GREEN_LED, LOW);
    finger.LEDcontrol(FINGERPRINT_LED_BREATHING, 100, FINGERPRINT_LED_BLUE);
  }
}

void checkFingerprint() {
  uint8_t p = finger.getImage();
  if (p != FINGERPRINT_OK) return;

  p = finger.image2Tz();
  if (p != FINGERPRINT_OK) return;

  p = finger.fingerFastSearch();
  if (p == FINGERPRINT_OK) {
    finger.LEDcontrol(FINGERPRINT_LED_FLASHING, 25, FINGERPRINT_LED_PURPLE, 3);
    Serial.print("FINGERPRINT_FOUND:");
    Serial.println(finger.fingerID);
    sessionActive = true;
  } else if (p == FINGERPRINT_NOTFOUND) {
    finger.LEDcontrol(FINGERPRINT_LED_FLASHING, 25, FINGERPRINT_LED_RED, 3);
    Serial.println("NEW_FINGERPRINT_DETECTED");
    sessionActive = true;
  }
}

void readSensorsAndSend() {
  long lastBeat = 0;
  int beatAvg = 0;
  int beatCount = 0;
  long beatSum = 0;

  // Variables for SpO2 calculation
  float irDC = 0, redDC = 0;
  float irAC = 0, redAC = 0;
  long irMax = 0, irMin = 1000000;
  long redMax = 0, redMin = 1000000;

  unsigned long startTime = millis();
  unsigned long lastWindowTime = millis();
  
  // 15-second active sampling window
  while (millis() - startTime < 15000) {
    long irValue = particleSensor.getIR();
    long redValue = particleSensor.getRed();

    if (irValue < 50000) { // Finger removed
      irMax = 0; irMin = 1000000;
      redMax = 0; redMin = 1000000;
      delay(10);
      continue;
    }

    // BPM Calculation using heartRate.h library
    if (checkForBeat(irValue) == true) {
      long delta = millis() - lastBeat;
      lastBeat = millis();
      float bpm = 60 / (delta / 1000.0);
      if (bpm > 40 && bpm < 200) {
        beatSum += bpm;
        beatCount++;
        beatAvg = beatSum / beatCount;
      }
    }

    // DC Component filtering (Exponential Moving Average)
    if (irDC == 0) irDC = irValue; else irDC = (0.95 * irDC) + (0.05 * irValue);
    if (redDC == 0) redDC = redValue; else redDC = (0.95 * redDC) + (0.05 * redValue);

    // Peak detection window (1 second) to find AC component
    if (millis() - lastWindowTime > 1000) {
      irAC = irMax - irMin;
      redAC = redMax - redMin;
      irMax = 0; irMin = 1000000;
      redMax = 0; redMin = 1000000;
      lastWindowTime = millis();
    }

    if (irValue > irMax) irMax = irValue;
    if (irValue < irMin) irMin = irValue;
    if (redValue > redMax) redMax = redValue;
    if (redValue < redMin) redMin = redValue;

    delay(10);
  }

  float temp = mlx.readObjectTempC();
  
  // Real SpO2 Calculation: Ratio of Ratios
  // SpO2 = 110 - 25 * R, where R = (redAC / redDC) / (irAC / irDC)
  int spo2 = 0;
  if (irDC > 0 && redDC > 0 && irAC > 10 && redAC > 10) {
    float R = (redAC / redDC) / (irAC / irDC);
    spo2 = (int)(110 - 25 * R);
    if (spo2 > 100) spo2 = 100;
    if (spo2 < 50) spo2 = 0; // Filter out noise
  }

  StaticJsonDocument<200> doc;
  doc["temp"] = temp;
  doc["bpm"] = beatAvg;
  doc["spo2"] = spo2;

  serializeJson(doc, Serial);
  Serial.println();
}
