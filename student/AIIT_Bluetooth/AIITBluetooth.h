// AIITBluetooth.h: HC-06 Bluetooth helper for Arduino Mega 2560.
// You don't need to change this file. Use it from your sketch:
//
//   #include "AIITBluetooth.h"
//   void setup() { bluetoothBegin("AIIT-01"); }
//   void loop()  { bluetoothUpdate(); }
//   void onMessage(String message) { send("I got: " + message); }
//
//   bluetoothBegin(name)  renames the HC-06 and starts Bluetooth (in setup)
//   bluetoothUpdate()     checks for messages (in loop, every time)
//   onMessage(message)    YOU write this; runs when the Mac sends a line
//   send(text)            sends a line to the Mac
//
// Wiring: HC-06 TXD -> pin 19, HC-06 RXD <- pin 18 (through a voltage
// divider), VCC -> 5V, GND -> GND. USB Serial Monitor at 115200 shows a log.

#pragma once
#include <Arduino.h>

// Written in your sketch.
void onMessage(String message);

const long AIIT_BT_BAUD = 9600;    // HC-06 factory speed
const long AIIT_USB_BAUD = 115200; // Serial Monitor speed
const int AIIT_MAX_NAME = 20;

void send(String text) {
  Serial1.println(text);
  Serial.print("Sent> ");
  Serial.println(text);
}

// Collect what the HC-06 says for a while (AT replies have no line ending).
String aiitReadHC06(unsigned long ms) {
  String reply = "";
  unsigned long start = millis();
  while (millis() - start < ms) {
    while (Serial1.available()) reply += (char)Serial1.read();
  }
  return reply;
}

bool aiitValidName(const char* name) {
  int n = strlen(name);
  if (n < 1 || n > AIIT_MAX_NAME) return false;
  for (int i = 0; i < n; i++) {
    char c = name[i];
    if (!(isAlphaNumeric(c) || c == '-' || c == '_')) return false;
  }
  return true;
}

// The HC-06 accepts AT commands only while nothing is connected to it.
// That's always true right after power-up, so we rename it on every start.
void aiitNameSensor(const char* name) {
  if (!aiitValidName(name)) {
    Serial.println("Sensor name must be 1-20 letters, digits, - or _. Not renamed.");
    return;
  }
  Serial1.print("AT");
  if (aiitReadHC06(1200).indexOf("OK") < 0) {
    Serial.println("HC-06 didn't answer AT. Something is connected to it, or");
    Serial.println("check wiring. Name not changed this time.");
    return;
  }
  // Older HC-06 firmware: AT+NAMExxx, no line ending.
  Serial1.print("AT+NAME");
  Serial1.print(name);
  String reply = aiitReadHC06(1500);
  if (reply.indexOf("OK") < 0) {
    // Newer firmware: AT+NAME=xxx with CR LF.
    Serial1.print("AT+NAME=");
    Serial1.print(name);
    Serial1.print("\r\n");
    reply = aiitReadHC06(1500);
  }
  if (reply.indexOf("OK") >= 0) {
    Serial.print("Sensor name: ");
    Serial.println(name);
  } else {
    Serial.print("Rename failed. HC-06 replied: ");
    Serial.println(reply);
  }
}

void bluetoothBegin(const char* name) {
  Serial.begin(AIIT_USB_BAUD);
  Serial1.begin(AIIT_BT_BAUD);
  delay(1000);  // give the HC-06 time to start
  aiitNameSensor(name);
  Serial.println("Bluetooth ready.");
}

String aiitIncoming = "";

void bluetoothUpdate() {
  while (Serial1.available()) {
    char c = Serial1.read();
    if (c == '\n' || c == '\r') {
      aiitIncoming.trim();
      if (aiitIncoming.length() > 0) {
        Serial.print("Got> ");
        Serial.println(aiitIncoming);
        String message = aiitIncoming;
        aiitIncoming = "";
        onMessage(message);
      }
      aiitIncoming = "";
    } else {
      aiitIncoming += c;
    }
  }
}
