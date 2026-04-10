void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
      // قراءة النص بالكامل حتى تصل علامة نهاية السطر
      String data = Serial.readStringUntil('\n');
    data.trim(); // تنظيف الفراغات الزائدة

    // الرد بنص آخر
    Serial.println("I received your string: " + data);
  }
}
