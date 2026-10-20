# HC-06 Bluetooth ↔ macOS

Control an Arduino Mega from a MacBook over an HC-06 Bluetooth module.

These steps start **after you've cloned this repository in VS Code** and
opened it. Setup is all **copy-paste commands** in VS Code's terminal,
written for a **school-managed MacBook**: no admin password and no Python
needed. Everything installs inside your home folder or this project folder.

How to use this page:

1. In VS Code, open a terminal: **Terminal → New Terminal** (or press
   ``Ctrl+` ``). It opens in the project folder.
2. For each step, copy the whole grey box, paste it into the terminal, press
   Return.
3. Find the text shown under **✅ Look for** in the output. If it isn't there,
   stop and check [Troubleshooting](#troubleshooting).

Always run the commands in a VS Code terminal opened this way, so they run in
the project folder.

The HC-06 is Bluetooth Classic, so iPhones and iPads can't connect to it.

---

## Setup (once per Mac)

### 0. Check you're in the project folder
```bash
ls
```
✅ Look for: `hc06.py`, `README.md` and `student` in the list.

### 1. Install uv (it installs Python for you)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
~/.local/bin/uv --version
```
✅ Look for: `everything's installed!` and then a line starting with `uv 0.`

### 2. Make the Python environment (venv)
```bash
~/.local/bin/uv venv --python 3.12
~/.local/bin/uv pip install -r requirements.txt
.venv/bin/python -c "import IOBluetooth; print('Bluetooth library OK')"
```
✅ Look for: `Creating virtual environment at: .venv`, then
`Installed … packages` (or `Checked … packages` if you've run it before),
then `Bluetooth library OK`.

The venv is a private Python inside the project folder, so nothing needs an
admin password. Git ignores it, so it never gets committed. If it ever
breaks, delete it with `rm -rf .venv` and repeat this step. If VS Code asks
whether to use this environment, you can click **Yes** or ignore it.

---

## Every new sensor

### 3. Name your sensor
Change `AIIT-07` to your own name before pasting: 1–20 letters, digits, `-`
or `_`, no spaces.
```bash
NAME=AIIT-07
sed -i '' "s/^const char SENSOR_NAME\[\] = \".*\";/const char SENSOR_NAME[] = \"$NAME\";/" student/AIIT_Bluetooth/AIIT_Bluetooth.ino
grep '^const char SENSOR_NAME' student/AIIT_Bluetooth/AIIT_Bluetooth.ino
```
✅ Look for: `const char SENSOR_NAME[] = "AIIT-07";` with **your** name.

### 4. Upload to the Mega
Plug the Mega into the MacBook with a USB cable, then:
```bash
.venv/bin/pio device list
.venv/bin/pio run -t upload
```
✅ Look for: a port starting with `/dev/cu.usbmodem` in the device list, then
`[SUCCESS]` at the end of the upload.

The first upload downloads the Arduino build tools (about 300 MB) and takes a
few minutes. Later uploads take seconds.

### 5. Check that the sensor renamed itself
```bash
.venv/bin/pio device monitor
```
✅ Look for: `Sensor name: AIIT-07` (your name) and `Bluetooth ready.`

Press `Ctrl+C` to leave the monitor.

### 6. Pair the sensor (the only step outside VS Code)
1. Open **System Settings → Bluetooth**.
2. If an old entry for this module is listed (`HC-06` or an older name), click
   **ⓘ → Forget This Device**. macOS remembers old names.
3. Find your sensor's name under **Nearby Devices** and click **Connect**.
   PIN: `1234` (or `0000`).

✅ Look for: your sensor's name under **My Devices**. "Not Connected" is
normal here.

### 7. Allow VS Code to use Bluetooth, and find your sensor
```bash
.venv/bin/python hc06.py --list
```
If macOS asks to let **Visual Studio Code** use Bluetooth, click **Allow**
and run the command again. If it asks for a PIN, enter `1234` (or `0000`).

✅ Look for: a line with your sensor's name, like
`98-d3-…  AIIT-07  (not connected)`.

If the command just hangs: **System Settings → Privacy & Security →
Bluetooth → Visual Studio Code** on, quit VS Code (`⌘Q`), reopen the project,
open a new terminal, and try again.

### 8. Send your first message
Use your sensor's name:
```bash
.venv/bin/python hc06.py --name AIIT-07 --send "LED ON"
```
✅ Look for: `Connected. The HC-06 LED should now be solid.` and then
`LED is ON`. The LED on pin 3 lights up.

Other commands:
```bash
.venv/bin/python hc06.py --name AIIT-07 --send "LED OFF"   # LED is OFF
.venv/bin/python hc06.py --name AIIT-07 --send "READ"      # A0 = <number>
.venv/bin/python hc06.py --name AIIT-07                    # chat: type lines, Ctrl+C to quit
.venv/bin/python hc06.py --name AIIT-07 --listen           # only receive
```

---

## Adding your own code

1. In VS Code's file list, open `student/AIIT_Bluetooth/AIIT_Bluetooth.ino`.
2. Replace the code (for example with code from Gemini). Keep:
   - `#include "AIITBluetooth.h"` at the top,
   - `bluetoothBegin(SENSOR_NAME);` as the first line of `setup()`,
   - `bluetoothUpdate();` in `loop()`,
   - an `onMessage(String message)` function.

   Use `send("text")` to send a line to the Mac. Don't edit `AIITBluetooth.h`.
3. Save (`⌘S`), then upload again (step 4). If the build fails, the error
   lines above `[FAILED]` say which line of your code is wrong.

---

## Before class: ask IT

On managed Macs these can be blocked. Ask IT to allow them before students start:

- [ ] **VS Code** installed, and **Git** available to it so students can clone.
      On a fresh Mac, VS Code's first clone asks to install Apple's developer
      tools; that install may need an admin password.
- [ ] Downloads from `astral.sh` and `github.com` (uv and its Python).
- [ ] Downloads from `pypi.org` and `files.pythonhosted.org` (Python packages).
- [ ] Downloads from `platformio.org` and its registry `*.registry.platformio.org`
      (Arduino build tools, step 4).
- [ ] Students can **pair Bluetooth devices** in System Settings.
- [ ] Students can allow **Visual Studio Code** under Privacy & Security →
      Bluetooth.

---

## Wiring

| HC-06 | Arduino Mega |
|---|---|
| TXD | pin 19 (RX1) |
| RXD | pin 18 (TX1), **through a voltage divider** (HC-06 RX is 3.3 V logic) |
| VCC | 5V |
| GND | GND |

LED: pin 3 → 220–330 Ω resistor → LED long leg; short leg → GND.

Built-in commands (case-insensitive): `LED ON`, `LED OFF`, `READ` (reports A0).
Anything else comes back as `I got: <MESSAGE>`.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Step 0 doesn't list `hc06.py` | The terminal isn't in the project folder. In VS Code, **File → Open Folder…** the cloned project, then open a new terminal. |
| `uv: command not found` | Use the full path `~/.local/bin/uv`, as in the steps. |
| `curl: (6) Could not resolve host` or a download stalls | No internet, or the school network blocks the site. See [Before class: ask IT](#before-class-ask-it). |
| `No such file or directory: .venv/bin/...` | Wrong folder (see step 0), or step 2 hasn't been done on this Mac. |
| Step 4: no `/dev/cu.usbmodem…` port | Try another USB cable (some only charge) or port. Avoid hubs. |
| Upload times out (`stk500v2_getsync`) | Another USB port or cable. Nothing wired to pins 0/1. Close any open monitor (`Ctrl+C`). |
| Step 5 shows `HC-06 didn't answer AT` | The HC-06 was connected to something when the Mega started, or TX/RX are swapped. Disconnect it, then press the Mega's reset button. |
| Step 5 shows `Rename failed` | Check the name: 1–20 letters, digits, `-` or `_`. |
| Old name still shows in Bluetooth | Forget the device and pair again (step 6). |
| `No paired device named …` | Pair it first (step 6), and type the name exactly as in step 3. |
| `Could not open the RFCOMM channel` | Another Mac or phone is connected to the sensor (only one at a time), or the sensor has no power. |
| `hc06.py` hangs with no output | VS Code needs Bluetooth permission (step 7). |

---

## For teachers

- `student/connect.html` is an experimental Chrome (Web Serial) page for
  talking to a paired sensor without a terminal. It hasn't been tested on
  hardware yet.
- Arduino IDE can open `student/AIIT_Bluetooth/` too (it's the same sketch
  PlatformIO builds; see `platformio.ini`).
- `rename_hc06.py` only works with the old USB passthrough firmware (in Git
  history) and isn't needed: the sketch renames the HC-06 from `SENSOR_NAME`.
