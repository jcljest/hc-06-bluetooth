# hc-06-bluetooth: notes for Claude

## One copy of the sketch

- `student/AIIT_Bluetooth/` is the only firmware. PlatformIO builds it
  directly (`src_dir` in `platformio.ini`); Arduino IDE opens the same folder.
  Don't recreate `src/main.cpp`.
- After changing the sketch, compile it: `.venv/bin/pio run`.
- Students edit only `AIIT_Bluetooth.ino` and `sensor_config.txt`
  (`SENSOR_NAME = …`, read by `hc06.py` and `controller.py`).
  `AIITBluetooth.h` holds the HC-06 plumbing (line reading, `send()`).

## Sensor names: teacher only

- Teachers name each HC-06 with `teacher/name_sensor.py` (AT+NAME, stored
  in the module). `teacher/` is committed so other teachers can use it; only
  the generated `teacher/name_sensor/sensor_name.h` is ignored. Never put
  renaming code back in the student sketch or student README steps.
- Editing `sensor_config.txt` in VS Code is an owner-approved GUI step,
  in addition to cloning and pairing.

## Setup instructions: fresh school-managed Mac, CLI only

Every setup step (README, student handouts) must work on a freshly installed,
school-managed MacBook: no admin password, no Python or developer tools, no
git, no Homebrew, and network filtering or MDM that may block downloads or
Bluetooth pairing.

- Setup is copy-paste Terminal commands. After each command, say exactly
  which text in the output proves it worked.
- Instructions start after the student has cloned the repo in VS Code and
  opened it; commands run in VS Code's integrated terminal (project folder).
  Don't add download/clone steps. Bluetooth permission is granted to
  Visual Studio Code.
- Never call `python3` directly: on a fresh Mac it opens Apple's
  developer-tools installer, which can need admin. Use `~/.local/bin/uv`
  (installed per user) to get Python and make the venv.
- Everything Python runs from the project venv: `.venv/bin/python`,
  `.venv/bin/pio`.
- The only GUI steps are cloning in VS Code, Bluetooth pairing, and editing
  `sensor_config.txt`.
- List any domain or permission IT has to allow.

## Other

- `controller.py` (game-controller window) and `hc06.py` send a blank line
  every 5 s (`KEEPALIVE_SECONDS`). Without it macOS puts the idle link in
  sniff mode, the HC-06 stops answering, and the link drops ~15 s after
  connecting. Keep it; `AIITBluetooth.h` ignores blank lines.
- Students connect by running these scripts, not by clicking Connect in
  System Settings (pairing there once is enough).
