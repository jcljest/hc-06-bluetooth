// Teacher tool: give the HC-06 a new Bluetooth name, then stop.
// Upload it with teacher/name_sensor.py, which writes the name into
// sensor_name.h. The HC-06 keeps the name after power-off.
//
// The HC-06 accepts AT commands only while nothing is connected to it over
// Bluetooth, which is always true right after power-up.

#include <Arduino.h>
#include "sensor_name.h"  // #define SENSOR_NAME "AIIT-YOURNAME"

const long BT_BAUD = 9600;    // HC-06 factory speed
const long USB_BAUD = 115200;

// Collect what the HC-06 says for a while (AT replies have no line ending).
String readHC06(unsigned long ms) {
  String reply = "";
  unsigned long start = millis();
  while (millis() - start < ms) {
    while (Serial1.available()) reply += (char)Serial1.read();
  }
  return reply;
}

void nameSensor(const char* name) {
  Serial1.print("AT");
  if (readHC06(1200).indexOf("OK") < 0) {
    Serial.println("HC-06 didn't answer AT. Something is connected to it, or");
    Serial.println("check wiring. Name not changed.");
    return;
  }
  // Older HC-06 firmware: AT+NAMExxx, no line ending.
  Serial1.print("AT+NAME");
  Serial1.print(name);
  String reply = readHC06(1500);
  if (reply.indexOf("OK") < 0) {
    // Newer firmware: AT+NAME=xxx with CR LF.
    Serial1.print("AT+NAME=");
    Serial1.print(name);
    Serial1.print("\r\n");
    reply = readHC06(1500);
  }
  if (reply.indexOf("OK") >= 0) {
    Serial.print("Sensor name: ");
    Serial.println(name);
  } else {
    Serial.print("Rename failed. HC-06 replied: ");
    Serial.println(reply);
  }
}

void setup() {
  Serial.begin(USB_BAUD);
  Serial1.begin(BT_BAUD);
  delay(1000);  // give the HC-06 time to start
  nameSensor(SENSOR_NAME);
}

void loop() {}
