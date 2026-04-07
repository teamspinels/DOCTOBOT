#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"

MAX30105 particleSensor;

const byte RATE_SIZE = 4; // عدد القراءات لحساب المتوسط
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;

float beatsPerMinute;
int beatAvg;

void setup()
{
  Serial.begin(115200);
  delay(1000);

  Serial.println("Initializing...");

  Wire.begin();

  if (!particleSensor.begin(Wire, I2C_SPEED_STANDARD))
  {
    Serial.println("MAX30102 not found ❌");
    while (1);
  }

  Serial.println("Sensor ready ✅");

  particleSensor.setup();
  particleSensor.setPulseAmplitudeRed(0x0A);
  particleSensor.setPulseAmplitudeIR(0x0A);
}

void loop()
{
  long irValue = particleSensor.getIR();

  // إذا تم اكتشاف نبضة
  if (checkForBeat(irValue) == true)
  {
    long delta = millis() - lastBeat;
    lastBeat = millis();

    beatsPerMinute = 60 / (delta / 1000.0);

    if (beatsPerMinute < 255 && beatsPerMinute > 20)
    {
      rates[rateSpot++] = (byte)beatsPerMinute;
      rateSpot %= RATE_SIZE;

      beatAvg = 0;
      for (byte x = 0; x < RATE_SIZE; x++)
        beatAvg += rates[x];

      beatAvg /= RATE_SIZE;
    }
  }

  Serial.print("IR=");
  Serial.print(irValue);
  Serial.print(" BPM=");
  Serial.print(beatsPerMinute);
  Serial.print(" Avg BPM=");
  Serial.print(beatAvg);

  if (irValue < 50000)
    Serial.print(" 👉 Put your finger");

  Serial.println();
}
