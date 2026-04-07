#include <Adafruit_Fingerprint.h>

#define mySerial Serial1

Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);

#define MAX_USERS 20

String names[MAX_USERS];
int currentID = 1;

// ===== قراءة اسم من Serial =====
String readName() {
  while (!Serial.available());
  return Serial.readStringUntil('\n');
}

// ===== تسجيل بصمة =====
bool enrollFingerprint(int id) {
  Serial.println("👉 Place finger...");
  while (finger.getImage() != FINGERPRINT_OK);

  if (finger.image2Tz(1) != FINGERPRINT_OK) return false;

  Serial.println("Remove finger...");
  delay(2000);
  while (finger.getImage() != FINGERPRINT_NOFINGER);

  Serial.println("Place same finger again...");
  while (finger.getImage() != FINGERPRINT_OK);

  if (finger.image2Tz(2) != FINGERPRINT_OK) return false;

  if (finger.createModel() != FINGERPRINT_OK) return false;

  if (finger.storeModel(id) != FINGERPRINT_OK) return false;

  return true;
}

void setup() {
  Serial.begin(115200);
  Serial1.begin(57600);

  if (!finger.verifyPassword()) {
    Serial.println("❌ Sensor error");
    while (1);
  }

  Serial.println("✅ System Ready");
}

void loop() {

  // محاولة قراءة بصمة
  if (finger.getImage() == FINGERPRINT_OK) {

    if (finger.image2Tz() == FINGERPRINT_OK) {

      if (finger.fingerSearch() == FINGERPRINT_OK) {

        int id = finger.fingerID;

        Serial.print("✅ Welcome: ");
        Serial.println(names[id]);

      } else {
        Serial.println("❌ Unknown finger!");

        Serial.println("Enter name to register:");
        String newName = readName();

        if (enrollFingerprint(currentID)) {
          names[currentID] = newName;

          Serial.print("✅ Registered ID ");
          Serial.print(currentID);
          Serial.print(" Name: ");
          Serial.println(newName);

          currentID++;
        } else {
          Serial.println("❌ Failed to enroll");
        }
      }
    }
  }

  delay(500);
}
