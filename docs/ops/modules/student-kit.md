---
module: student-kit
health: yellow
updated: 2026-10-16
---

# Student Kit

## Purpose

Let students on fresh MacBooks (no Python, no installs beyond Arduino IDE and
Chrome) name their HC-06, upload one sketch, and talk to their own sensor.

## Inputs

- Arduino Mega 2560 + HC-06 wired by the student (HC-06 on Serial1, pins 18/19).
- Student code pasted from a Gemini Gem into the marked section of the sketch.

## Outputs

- `student/AIIT_Bluetooth/AIIT_Bluetooth.ino`: one-file sketch.
- `student/connect.html`: Chrome Web Serial page for talking to the sensor.

## Interfaces / Contracts

- Messages are text lines ending in `\n` (the page also accepts `\r\n`).
- HC-06 link speed 9600 baud; USB Serial 115200 for logging.

## Invariants

- Students edit only `SENSOR_NAME` and the "YOUR CODE" section.

## Dependencies

- Chrome support for Bluetooth Classic (RFCOMM) ports in Web Serial on macOS. Unverified.

## Non-goals

- iPhone/BLE support, Uno support, replacing `hc06.py` for the owner.

## Current Health

**Yellow**

Reason: the Chrome-on-macOS Bluetooth path is untested on hardware.

## Active Sprints

- 2026-10-16-student-kit-one-file-mac

## Risks

- If Chrome can't open the HC-06 link on macOS, fall back to a small native Mac app.
