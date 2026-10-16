# hc-06-bluetooth: notes for Claude

## Arduino IDE and PlatformIO versions must match

- `student/AIIT_Bluetooth/AIIT_Bluetooth.ino` (students, Arduino IDE) and
  `src/main.cpp` (PlatformIO) are the same program and must stay
  byte-identical. Whenever you change one, make the same change to the other
  in the same turn.
- Both include `student/AIIT_Bluetooth/AIITBluetooth.h`. There is one copy
  of it; PlatformIO finds it through `build_flags` in `platformio.ini`.
  Never copy it into `src/`.
- A PostToolUse hook (`scripts/check_sketch_sync.py`) flags any edit that
  leaves the two files different. Check by hand with
  `python3 scripts/check_sketch_sync.py`.
- After changing either, compile both:
  `.venv/bin/pio run` and
  `"/Applications/Arduino IDE.app/Contents/Resources/app/lib/backend/resources/arduino-cli" compile --fqbn arduino:avr:mega student/AIIT_Bluetooth`.

## Setup instructions assume a fresh school-managed Mac

Every setup step (README, student handouts) must work on a freshly installed,
school-managed MacBook: no admin password, no Python or developer tools, no
Homebrew, apps possibly only from the school's app store (Self Service), and
network filtering or MDM policies that may block downloads, Bluetooth pairing
or Chrome's serial access. Write numbered steps with a "you should see" check
after each, and list anything IT has to allow.

## Student kit

- Students edit only `AIIT_Bluetooth.ino`. `AIITBluetooth.h` holds the HC-06
  plumbing (rename on boot, line reading, `send()`).
- `student/connect.html` is the Chrome (Web Serial) page for talking to a
  sensor. Don't publish it online without the owner's approval.
