// AIIT Bluetooth starter (Arduino Mega 2560 + HC-06)
//
// 1. Change SENSOR_NAME to your sensor's name.
// 2. Write your code below. The Bluetooth parts live in the AIITBluetooth.h
//    tab. Don't change that tab.
// 3. Upload. Pair your sensor on the Mac (System Settings > Bluetooth,
//    PIN 1234), then open connect.html in Chrome.
//
//   send("text")         sends a line to the Mac
//   onMessage(message)   runs every time the Mac sends a line

#include "AIITBluetooth.h"

// 1-20 characters: letters, digits, - or _. No spaces.
const char SENSOR_NAME[] = "AIIT-01";

const int LED_PIN = 3;

void setup() {
  bluetoothBegin(SENSOR_NAME);  // keep this first
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
}

void loop() {
  bluetoothUpdate();  // keep this; it checks for messages
  // Your code here runs over and over. Avoid long delay() calls,
  // or messages will wait until the delay ends.
}

void onMessage(String message) {
  message.toUpperCase();
  if (message == "LED ON") {
    digitalWrite(LED_PIN, HIGH);
    send("LED is ON");
  } else if (message == "LED OFF") {
    digitalWrite(LED_PIN, LOW);
    send("LED is OFF");
  } else if (message == "READ") {
    send("A0 = " + String(analogRead(A0)));
  } else {
    send("I got: " + message);
  }
}
