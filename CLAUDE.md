# hc-06-bluetooth: notes for Claude

## One copy of the sketch

- `student/AIIT_Bluetooth/` is the only firmware. PlatformIO builds it
  directly (`src_dir` in `platformio.ini`); Arduino IDE opens the same folder.
  Don't recreate `src/main.cpp`.
- After changing the sketch, compile it: `.venv/bin/pio run`.
- Students edit only `AIIT_Bluetooth.ino`. `AIITBluetooth.h` holds the HC-06
  plumbing (rename on boot, line reading, `send()`).

## Setup instructions: fresh school-managed Mac, CLI only

Every setup step (README, student handouts) must work on a freshly installed,
school-managed MacBook: no admin password, no Python or developer tools, no
git, no Homebrew, and network filtering or MDM that may block downloads or
Bluetooth pairing.

- Setup is copy-paste Terminal commands. After each command, say exactly
  which text in the output proves it worked.
- Never call `python3` or `git` directly: on a fresh Mac they open Apple's
  developer-tools installer, which can need admin. Use `~/.local/bin/uv`
  (installed per user) to get Python and make the venv, and `curl` + `unzip`
  (built into macOS) to get the code.
- Everything Python runs from the project venv: `.venv/bin/python`,
  `.venv/bin/pio`.
- The only GUI step is Bluetooth pairing (System Settings).
- List any domain or permission IT has to allow.

## Other

- `student/connect.html` is an untested Chrome (Web Serial) option. Don't
  publish it online without the owner's approval.
