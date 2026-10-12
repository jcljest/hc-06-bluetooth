#include <Arduino.h>

// HC-06 Bluetooth control for Arduino Mega 2560.
// HC-06 on Serial1 (pin 19 RX1, pin 18 TX1). USB Serial is free for logging.
//
// Bluetooth commands (one per line, case-insensitive):
//   LED ON      turn on the LED on pin 3
//   LED OFF     turn it off
//   LED TOGGLE  flip it
//   LED         report its state
// Anything else is echoed back as "Mega got: <line>".
// Every line is logged to USB Serial as "BT> <line>".
// USB Serial -> HC-06: anything typed in Serial Monitor goes to the HC-06.
// While Bluetooth is connected it is sent to the Mac; while disconnected the
// HC-06 treats it as AT commands (see rename_hc06.py) and its replies are
// logged to USB as "HC06> <reply>".

const long BT_BAUD = 9600;    // HC-06 factory default
const long USB_BAUD = 115200;
const int LED_PIN = 3;

String line;
unsigned long lastByteMs = 0;

void setLed(bool on) {
  digitalWrite(LED_PIN, on ? HIGH : LOW);
}

void reportLed() {
  Serial1.println(digitalRead(LED_PIN) ? "LED is ON" : "LED is OFF");
}

void handleLine(String cmd) {
  cmd.trim();
  Serial.print("BT> ");
  Serial.println(cmd);
  cmd.toUpperCase();

  if (cmd == "LED ON") {
    setLed(true);
    reportLed();
  } else if (cmd == "LED OFF") {
    setLed(false);
    reportLed();
  } else if (cmd == "LED TOGGLE") {
    setLed(!digitalRead(LED_PIN));
    reportLed();
  } else if (cmd == "LED") {
    reportLed();
  } else {
    Serial1.print("Mega got: ");
    Serial1.println(cmd);
  }
}

void setup() {
  pinMode(LED_PIN, OUTPUT);
  setLed(false);
  Serial.begin(USB_BAUD);
  Serial1.begin(BT_BAUD);
  Serial.println("hc06 LED control ready");
}

void loop() {
  while (Serial1.available()) {
    char c = Serial1.read();
    lastByteMs = millis();
    if (c == '\n') {
      handleLine(line);
      line = "";
    } else {
      line += c;
    }
  }
  // AT replies from the HC-06 itself ("OK", "OKsetname") have no newline.
  // Show any unterminated text on USB once the HC-06 goes quiet.
  if (line.length() > 0 && millis() - lastByteMs > 300) {
    Serial.print("HC06> ");
    Serial.println(line);
    line = "";
  }
  while (Serial.available()) {
    Serial1.write(Serial.read());
  }
}
