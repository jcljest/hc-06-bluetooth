// AIIT Bluetooth starter (Arduino Mega 2560 + HC-06)
//
// 1. Write your code below. The Bluetooth parts live in the AIITBluetooth.h
//    tab. Don't change that tab.
// 2. Upload. Pair your sensor on the Mac (System Settings > Bluetooth,
//    PIN 1234), then run:  .venv/bin/python controller.py
//
//   send("text")         sends a line to the Mac
//   onMessage(message)   runs every time the Mac sends a line
//
// The controller window sends one line per button:
//   pressed:  UP  DOWN  LEFT  RIGHT  K  L
//   let go:   UP RELEASED  DOWN RELEASED  ...  L RELEASED

#include "AIITBluetooth.h"

const int LED_PIN = 3;
const int K_PIN = 2;

void setup() {
  bluetoothBegin();  // keep this first
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  pinMode(K_PIN, OUTPUT);
  digitalWrite(K_PIN, LOW);
}

void loop() {
  bluetoothUpdate();  // keep this; it checks for messages
  // Your code here runs over and over. Avoid long delay() calls,
  // or messages will wait until the delay ends.
}

void onMessage(String message) {
  message.toUpperCase();
  if (message == "K") {
    digitalWrite(K_PIN, HIGH);   // pin 2 on while K is held
    send("Pin 2 HIGH");
  } else if (message == "K RELEASED") {
    digitalWrite(K_PIN, LOW);    // pin 2 off when K is let go
    send("Pin 2 LOW");
  } else if (message == "LED ON") {
    digitalWrite(LED_PIN, HIGH);
    send("LED is ON");
  } else if (message == "L" || message == "LED OFF") {
    digitalWrite(LED_PIN, LOW);
    send("LED is OFF");
  } else if (message == "UP" || message == "READ") {
    send("A0 = " + String(analogRead(A0)));
  } else if (message == "DOWN") {
    digitalWrite(LED_PIN, HIGH);  // LED stays on while DOWN is held
  } else if (message == "DOWN RELEASED") {
    digitalWrite(LED_PIN, LOW);
  } else if (message.endsWith(" RELEASED")) {
    // Other buttons let go: nothing to do yet.
  } else {
    send("I got: " + message);  // LEFT and RIGHT end up here. Add your own!
  }
}
