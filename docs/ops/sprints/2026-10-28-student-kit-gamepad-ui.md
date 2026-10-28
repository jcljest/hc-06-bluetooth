---
id: 2026-10-28-student-kit-gamepad-ui
module: student-kit
status: done
health: green
owner_session: null
worktree: /Users/laij/Projects/hc-06-bluetooth
started: 2026-10-28
updated: 2026-10-28
base_commit: 626b995
depends_on: []
blocks: []
---

# Game-controller UI for the sensor

## Objective

A window that looks like a simple game controller (D-pad + A/B buttons) and
sends one text line per button over the HC-06 link. Students change only the
Arduino sketch to decide what each button does.

## Why This Matters

Students can control their sensor without typing commands in a terminal. All
the work they do is in `AIIT_Bluetooth.ino`.

## Scope

- `controller.py`: Tk window that reuses `hc06.py`'s IOBluetooth connection.
  It sends `UP`/`DOWN`/`LEFT`/`RIGHT`/`A`/`B` when a button is pressed and
  `<BUTTON> RELEASED` when it is let go. Clicks and keyboard both work (arrows,
  Z/X). It shows the sensor's replies in the window and, when `--name` isn't
  given, reads the sensor name from the sketch.
- Starter sketch: `onMessage` handles the controller buttons.
- README: a step for running the controller and the message table.

## Non-goals

- Analog sticks, more buttons, BLE/iPhone, a web or Chrome version.
- Changing `AIITBluetooth.h`.

## Acceptance Criteria

- [x] `controller.py` starts and shows the D-pad and the A/B buttons. It shows
      a clear error instead of crashing if the sensor isn't paired. (Window
      built and driven by a script; nobody has looked at it yet. See Risks.)
- [x] Each press sends exactly one line (no repeats from key auto-repeat), and
      each release sends one `… RELEASED` line.
- [x] The starter sketch compiles (`.venv/bin/pio run` SUCCESS) and responds
      to the controller buttons (compile only; not run on hardware).
- [x] README step 9 has copy-paste command + "Look for" text (fresh-Mac rules).
- [x] ~~Hardware test: the buttons work on a real HC-06 (owner).~~ Waived by the
      owner 2026-10-28 ("assume the hardware will work as intended"). NOT verified:
      controller.py on a sensor, automatic keepalive, teacher/name_sensor.py.

## Plan

1. Write controller.py, reusing hc06.py helpers.
2. Update the starter sketch's onMessage.
3. Update the README.
4. Verify: compile, launch the UI with a fake channel, test key-repeat handling.

## Progress / Checkpoints

### 2026-10-28
- Sprint started.
- Added controller.py, updated the starter sketch's onMessage (A/B/UP/DOWN +
  RELEASED; kept LED ON/LED OFF/READ for step 8), README step 9 + troubleshooting row.

## Files Changed

- New: `controller.py`, `sensor_config.txt`, `teacher/` (README, name_sensor.py,
  naming_config.txt, name_sensor/), `.vscode/settings.json`
- Changed: `hc06.py` (config name, keepalive), `student/AIIT_Bluetooth/*`
  (no rename; K/L handlers), `README.md`, `CLAUDE.md`, `.gitignore`,
  `requirements.txt`, `docs/ops/modules/student-kit.md`
- Deleted: `student/connect.html`, `rename_hc06.py`

## Verification Evidence

### Commands Run

```text
.venv/bin/pio run                                   -> [SUCCESS]
uv venv --python 3.12 (scratch) + pyobjc-framework-IOBluetooth; Tk 9.0
scratch test_controller.py (FakeLink, scripted presses/keys) -> ALL TESTS PASSED
Link('AIIT-NO-SUCH').open() -> "No paired device named AIIT-NO-SUCH. ... click Reconnect."
```

### Results

- Mouse press/release for all 6 buttons -> exactly BUTTON, BUTTON RELEASED.
- Key auto-repeat (press + release/press pairs) -> one UP, one UP RELEASED.
- Z/X map to A/B; focus loss releases held buttons; replies show as "← …";
  partial reply lines are buffered until the newline arrives.
- SENSOR_NAME read from the sketch (AIIT-10-laij).
- The owner's local .venv (Apple Python 3.9, Tk 8.5) hangs on any Tk
  `update()`, even a bare window. uv's Python 3.12 (README step 2) works.
- Screenshot not captured (no screen-recording permission), so the look is unchecked.

## Decisions

- 2026-10-28 (owner): the teacher names sensors; students can't. Rename code
  moved out of `AIITBluetooth.h` (`bluetoothBegin()` now takes no name) into a
  git-ignored `teacher/` tool (`name_sensor.py` uploads `teacher/name_sensor/`,
  checks for `Sensor name: X` on the USB log, then re-uploads the starter).
  Students put the label name in `sensor_config.txt`; `hc06.py` and
  `controller.py` read it. README steps 3/5/6/8/9 rewritten.
- 2026-10-28 (owner): `student/connect.html` deleted.
- 2026-10-28 (owner): `teacher/` is committed (not ignored) so other teachers
  can use it; `teacher/name_sensor/sensor_name.h` stays ignored. Students can
  see the tool; the starter sketch still has no rename code.
- 2026-10-28 (owner): the naming tool reads `teacher/naming_config.txt`
  (`SENSOR_NAME = …`, same format and reader as `sensor_config.txt`:
  `hc06.configured_name(path)`). A name on the command line overrides it.
  Tested with upload/port stubbed: placeholder/missing/bad names stop with a
  message; config name and CLI override are accepted.
- Python/Tk window, not a Chrome page. Opening `/dev/cu.*` doesn't bring up
  the HC-06 link on recent macOS (see `hc06.py`), so it reuses the IOBluetooth
  path that's known to work.

## Dependency Changes

- Needs Tk in the venv's Python. uv's Python includes it.

## Risks / Blockers

- Not hardware-tested: the RFCOMM link from the Tk window still needs a real HC-06.
- Unchecked: does IOBluetooth deliver data while Tk's event loop runs?
  (controller.py also calls hc06.pump(0) every 20 ms.)
- The owner's current .venv is Apple Python 3.9; recreate it per README step 2.
- 2026-10-28 hardware: AIIT-10-laij drops ~15 s after connecting, even with
  hc06.py holding RFCOMM open. In the macOS log (09:31), the RFCOMM channel
  opens at 39.6 s. After 10 s idle the link enters sniff mode (interval 800).
  Exactly 5 s later it's disconnected (STATUS 708 / reason 328). Python closed
  it only after the drop. The likely cause is that the HC-06 stops answering
  in sniff mode. Unverified fix: Mac sends a blank-line keepalive every ~5 s
  (AIITBluetooth.h ignores blank lines). Owner to test by pressing Return
  every few seconds in hc06.py.
- 2026-10-28: owner confirmed that pressing Return every few seconds keeps
  the link up. Added `KEEPALIVE_SECONDS = 5` blank-line keepalive to hc06.py
  (interactive and --listen) and controller.py (`Link.poll`; not shown in
  the log). Scripted test: idle link -> only blank lines at the interval;
  busy link -> no keepalives. Not yet run on hardware with the automatic
  keepalive (owner: run hc06.py idle for 2 min).
- 2026-10-28: at the owner's request, the buttons are now K and L (labels and
  messages `K`/`L`/`K RELEASED`/`L RELEASED`). D-pad keys are arrows + WASD;
  Z/X removed. The sketch has the owner's pin-2 code (A_PIN -> K_PIN, "A" -> "K",
  "B" -> "L"). README step 9 updated. `pio run` SUCCESS; scripted UI tests
  (incl. WASD, caps lock, K/L) pass.
- 2026-10-28: teacher-naming change (see Decisions). Verified: student sketch
  and naming sketch `pio run` SUCCESS; config parser cases (placeholder,
  missing, spacing, commented) pass; both scripts exit with "No sensor name
  yet" on the placeholder; naming tool's name check and log check pass. NOT
  run on hardware: `teacher/name_sensor.py` (the owner's sensor wasn't
  renamed without asking).

## Human Decision Needed

- None.

## Handoff

### Outcome
Controller window, starter sketch, and README step 9 written. Verified by
compiling and by scripted tests. Not run on hardware.

### Current State
done. Merged to main and pushed 2026-10-28. The owner waived the hardware
criterion; the hardware paths above are unverified.

### Next Action
None. If a hardware problem shows up in class, open a new sprint: start
with the controller keepalive and teacher/name_sensor.py, which never ran on
a sensor.
