---
module: student-kit
health: yellow
updated: 2026-10-28
---

# Student Kit

## Purpose

Let students on fresh school MacBooks (no admin; Python via uv in a project
venv) name their HC-06, upload one sketch, and talk to their own sensor from
the terminal (`hc06.py`) or a game-controller window (`controller.py`).

## Inputs

- Arduino Mega 2560 + HC-06 wired by the student (HC-06 on Serial1, pins 18/19).
- HC-06 already named and labeled by the teacher (`teacher/name_sensor.py`).
- Student code pasted from a Gemini Gem into the marked section of the sketch.

## Outputs

- `student/AIIT_Bluetooth/AIIT_Bluetooth.ino`: one-file sketch (`bluetoothBegin()`, no rename).
- `sensor_config.txt`: `SENSOR_NAME = …`; the scripts' default sensor name.
- `hc06.py`: terminal chat with the sensor over IOBluetooth RFCOMM.
- `controller.py`: D-pad + K/L window; one line per press, `<BUTTON> RELEASED` on release.

## Interfaces / Contracts

- Messages are text lines ending in `\n`; replies may end in `\r\n`.
- Controller messages: `UP DOWN LEFT RIGHT K L`, and `<name> RELEASED`.
- The Mac sends a blank-line keepalive every 5 s; the sketch must ignore blank lines (AIITBluetooth.h does).
- HC-06 link speed 9600 baud; USB Serial 115200 for logging.

## Invariants

- Students edit only `AIIT_Bluetooth.ino` and `sensor_config.txt`.
- The student kit never renames the HC-06; only the teacher tool does.

## Dependencies

- macOS IOBluetooth via PyObjC; Tk in uv's Python (3.12, Tk 9.0).

## Non-goals

- iPhone/BLE support, Uno support, replacing `hc06.py` for the owner.

## Current Health

**Yellow**

Reason: the link works on hardware with hc06.py (owner, 2026-10-28). The owner
waived hardware tests for the automatic keepalive, controller.py and
teacher/name_sensor.py, so those are unverified.

## Active Sprints

- 2026-10-16-student-kit-one-file-mac
- (done) 2026-10-28-student-kit-gamepad-ui

## Risks

- The HC-06 drops the link in macOS sniff mode; the keepalive works around it.
- `student/connect.html` (Chrome Web Serial) deleted 2026-10-28, owner decision: never tested; replaced by controller.py.
