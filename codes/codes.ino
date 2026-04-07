#include <Wire.h>
#include <Adafruit_Fingerprint.h>
#include <MAX30105.h>
#include "heartRate.h"
#include <Adafruit_MLX90614.h>

#define RED_LED 5
#define YELLOW_LED 6
#define GREEN_LED 7

// ===== Sensors =====
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&Serial1);
MAX30105 particleSensor;
Adafruit_MLX90614 mlx = Adafruit_MLX90614();

// ===== Heart =====
long lastBeat = 0;
float bpm = 0;
float spo2 = 0;

// ===== Setup =====
void setup() {
  Serial.begin(115200);
  Serial1.begin(57600);
  Wire.begin();

  pinMode(RED_LED, OUTPUT);
  pinMode(YELLOW_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);

  finger.begin(57600);
  particleSensor.begin(Wire, I2C_SPEED_STANDARD);
  particleSensor.setup();
  mlx.begin();

  Serial.println("SYSTEM READY");
}

// ===== Fingerprint =====
void getFingerprint() {
  if (finger.getImage() != FINGERPRINT_OK) {
    Serial.println("{\"fingerprint\":\"none\"}");
    return;
  }

  if (finger.image2Tz() != FINGERPRINT_OK) return;

  if (finger.fingerSearch() == FINGERPRINT_OK) {
    Serial.print("{\"fingerprint_id\":");
    Serial.print(finger.fingerID);
    Serial.println("}");
  } else {
    Serial.println("{\"fingerprint\":\"not_found\"}");
  }
}

// ===== Temperature =====
void getTemperature() {
  Serial.println("{");
  for (int i = 0; i < 5; i++) {
    float temp = mlx.readObjectTempC();

    Serial.print("\"read ");
    Serial.print(i + 1);
    Serial.print("\": ");
    Serial.print(temp);

    if (i < 4) Serial.println(",");
    delay(200);
  }
  Serial.println("}");
}

// ===== Heart =====
void getHeart() {
  float avgBPM = 0;
  int count = 0;

  for (int i = 0; i < 100; i++) {
    long irValue = particleSensor.getIR();

    if (checkForBeat(irValue)) {
      long delta = millis() - lastBeat;
      lastBeat = millis();

      bpm = 60 / (delta / 1000.0);

      if (bpm > 40 && bpm < 180) {
        avgBPM += bpm;
        count++;
      }
    }
    delay(20);
  }

  if (count > 0) avgBPM /= count;

  // SPO2 fake approx (for demo)
  spo2 = 95 + random(-2, 2);

  Serial.print("{\"BPM\":");
  Serial.print(avgBPM);
  Serial.print(",\"SpO2\":");
  Serial.print(spo2);
  Serial.println("}");
}

// ===== LEDs =====
void controlLED(String cmd) {
  digitalWrite(RED_LED, cmd == "LightR");
  digitalWrite(YELLOW_LED, cmd == "LightY");
  digitalWrite(GREEN_LED, cmd == "LightG");

  Serial.println("{\"LED\":\"OK\"}");
}

// ===== Main Loop =====
void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "Get Fingerprint") {
      getFingerprint();
    }
    else if (cmd == "Get body temp") {
      getTemperature();
    }
    else if (cmd == "Get Heartbeat and Spo2") {
      getHeart();
    }
    else if (cmd == "LightR" || cmd == "LightY" || cmd == "LightG") {
      controlLED(cmd);
    }
    else {
      Serial.println("{\"error\":\"unknown_command\"}");
    }
  }
}
