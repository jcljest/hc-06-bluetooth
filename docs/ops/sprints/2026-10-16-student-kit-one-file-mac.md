---
id: 2026-10-16-student-kit-one-file-mac
module: student-kit
status: active
health: yellow
owner_session: null
worktree: /Users/laij/Projects/hc-06-bluetooth
started: 2026-10-16
updated: 2026-10-16
base_commit: 5605f34
depends_on: []
blocks: []
---

# One-file student kit for fresh MacBooks

## Objective

One Arduino sketch that names the HC-06 itself, plus a Chrome page that finds
and talks to that named sensor, with nothing else to install.

## Why This Matters

Students use free Gemini and fresh MacBooks. `hc06.py` and `rename_hc06.py`
need Python + PyObjC, which these machines don't have.

## Scope

- `student/AIIT_Bluetooth/` sketch folder (Mega): `AIITBluetooth.h` holds all HC-06 plumbing (auto-rename on boot, line reading, `send()`); `AIIT_Bluetooth.ino` is student code only (`SENSOR_NAME`, standard `setup()`/`loop()`, `onMessage()`, LED example). Same files build in Arduino IDE and PlatformIO.
- `student/connect.html`: Web Serial page, pick sensor, send lines, see replies.

## Non-goals

- Gemini Gem instructions and student handout (next sprint).
- Native Mac app fallback (only if Chrome test fails).
- Publishing the page online.

## Acceptance Criteria

- [x] Sketch compiles for Arduino Mega 2560 (Arduino IDE CLI and PlatformIO).
- [ ] Owner uploads it with a new `SENSOR_NAME`; the module shows that name in Bluetooth settings after Forget + re-pair.
- [ ] `hc06.py --name <NAME> --send "LED ON"` lights the LED (regression check against existing tool).
- [ ] In Chrome on macOS, `connect.html` lists the paired sensor, connects, and `LED ON` / `LED OFF` work with replies shown.

## Plan

1. Write sketch; compile with PlatformIO (`.venv/bin/pio`) against megaatmega2560.
2. Write connect.html.
3. Owner runs hardware tests; record results.

## Progress / Checkpoints

### 2026-10-16
- Sprint started.
- Wrote `student/AIIT_Bluetooth/AIIT_Bluetooth.ino` and `student/connect.html` (uncommitted).
- Owner asked for maximum modularity: split plumbing into `AIITBluetooth.h` tab. Decision: students use Arduino IDE (PlatformIO needs Python/CLT and ~150 MB toolchain per fresh Mac); owner may use PlatformIO with the same files.
- Owner asked that the Arduino IDE and PIO versions always be updated together. `src/main.cpp` is now a byte-identical copy of `AIIT_Bluetooth.ino` (old passthrough firmware is in Git history at 5605f34; `rename_hc06.py` no longer works with it). PIO finds the shared header via `build_flags = -I student/AIIT_Bluetooth`. Added `scripts/check_sketch_sync.py` as a project PostToolUse hook in `.claude/settings.json`, plus `CLAUDE.md` rule. Tested: both builds pass; hook exits 0 in sync / unrelated file, exits 2 with message on drift.
- Owner asked that the hook also run when Claude starts in `~/Projects`. Added the same check to user-level `~/.claude/settings.json` (skips when CLAUDE_PROJECT_DIR is this repo, to avoid running twice; skips if the script is missing). Proved live: a test edit to `src/main.cpp` triggered the hook in a `~/Projects` session; edit reverted, files back in sync.
- Owner constraint: all setup instructions target fresh, school-managed MacBooks (no admin, no dev tools, MDM/network policies). Recorded in `CLAUDE.md`. Rewrote README as path A (students: Self Service Arduino IDE → upload → pair → Chrome) and path B (teacher: Command Line Tools → clone → venv → Bluetooth permission → `--list` → `--send`), each step with a "You should see" check, plus an IT checklist and troubleshooting table. Step A6 marked untested.

## Verification Evidence

### Commands Run

```text
.venv/bin/pio ci student/AIIT_Bluetooth --board megaatmega2560
"/Applications/Arduino IDE.app/.../arduino-cli" compile --fqbn arduino:avr:mega student/AIIT_Bluetooth
node --check <script extracted from connect.html>
```

### Results

- Split sketch: both compilers succeed. Flash 6732 B (2.7%), RAM 683 B (8.3%).
- connect.html script: syntax OK. Not yet run against hardware.
- Uncertain: whether Chrome on macOS 26 opens the HC-06 RFCOMM link. Verified only by the owner's hardware test.

## Next Action

Owner: upload the sketch with a new SENSOR_NAME, re-pair, then try connect.html
in Chrome. Report what the chooser shows and whether LED ON works.
