// AIITBluetooth.h: HC-06 Bluetooth helper for Arduino Mega 2560.
// You don't need to change this file. Use it from your sketch:
//
//   #include "AIITBluetooth.h"
//   void setup() { bluetoothBegin(); }
//   void loop()  { bluetoothUpdate(); }
//   void onMessage(String message) { send("I got: " + message); }
//
//   bluetoothBegin()      starts Bluetooth (first line of setup)
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

void send(String text) {
  Serial1.println(text);
  Serial.print("Sent> ");
  Serial.println(text);
}

// The sensor's name is stored in the HC-06 itself (your teacher set it).
void bluetoothBegin() {
  Serial.begin(AIIT_USB_BAUD);
  Serial1.begin(AIIT_BT_BAUD);
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
