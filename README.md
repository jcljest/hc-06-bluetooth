# HC-06 Bluetooth ↔ macOS

Control an Arduino Mega from a MacBook over an HC-06 Bluetooth module.

Setup is all **copy-paste Terminal commands**, written for a **fresh,
school-managed MacBook**: no admin password, no Python, no developer tools,
no git. Everything installs inside your home folder.

How to use this page:

1. Open **Terminal** (Spotlight: press `⌘ Space`, type `Terminal`, press Return).
2. For each step, copy the whole grey box, paste it into Terminal, press Return.
3. Find the text shown under **✅ Look for** in the output. If it isn't there,
   stop and check [Troubleshooting](#troubleshooting).

Commands that begin with `.venv/` must be run from the project folder. Step 3
puts you there; after closing Terminal, run `cd ~/Documents/hc-06-bluetooth-main`
first.

The HC-06 is Bluetooth Classic, so iPhones and iPads can't connect to it.

---

## Setup (once per Mac)

### 1. Install uv (it installs Python for you)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
~/.local/bin/uv --version
```
✅ Look for: `everything's installed!` and then a line starting with `uv 0.`

### 2. Download the project
```bash
cd ~/Documents
curl -L -o hc-06-bluetooth.zip https://github.com/jcljest/hc-06-bluetooth/archive/refs/heads/main.zip
unzip -o -q hc-06-bluetooth.zip
cd hc-06-bluetooth-main
ls
```
✅ Look for: `hc06.py`, `README.md` and `student` in the list.

> Running step 2 again replaces your edited sketch. Copy
> `student/AIIT_Bluetooth/AIIT_Bluetooth.ino` somewhere safe first.

### 3. Make the Python environment (venv)
```bash
cd ~/Documents/hc-06-bluetooth-main
~/.local/bin/uv venv --python 3.12
~/.local/bin/uv pip install -r requirements.txt
.venv/bin/python -c "import IOBluetooth; print('Bluetooth library OK')"
```
✅ Look for: `Creating virtual environment at: .venv`, then
`Installed … packages` (or `Checked … packages` if you've run it before),
then `Bluetooth library OK`.

The venv is a private Python inside the project folder, so nothing needs an
admin password. If it ever breaks, delete it with `rm -rf .venv` and repeat
this step.

---

## Every new sensor

### 4. Name your sensor
Change `AIIT-07` to your own name before pasting: 1–20 letters, digits, `-`
or `_`, no spaces.
```bash
cd ~/Documents/hc-06-bluetooth-main
NAME=AIIT-07
sed -i '' "s/^const char SENSOR_NAME\[\] = \".*\";/const char SENSOR_NAME[] = \"$NAME\";/" student/AIIT_Bluetooth/AIIT_Bluetooth.ino
grep '^const char SENSOR_NAME' student/AIIT_Bluetooth/AIIT_Bluetooth.ino
```
✅ Look for: `const char SENSOR_NAME[] = "AIIT-07";` with **your** name.

### 5. Upload to the Mega
Plug the Mega into the MacBook with a USB cable, then:
```bash
cd ~/Documents/hc-06-bluetooth-main
.venv/bin/pio device list
.venv/bin/pio run -t upload
```
✅ Look for: a port starting with `/dev/cu.usbmodem` in the device list, then
`[SUCCESS]` at the end of the upload.

The first upload downloads the Arduino build tools (about 300 MB) and takes a
few minutes. Later uploads take seconds.

### 6. Check that the sensor renamed itself
```bash
cd ~/Documents/hc-06-bluetooth-main
.venv/bin/pio device monitor
```
✅ Look for: `Sensor name: AIIT-07` (your name) and `Bluetooth ready.`

Press `Ctrl+C` to leave the monitor.

### 7. Pair the sensor (the only step that isn't in Terminal)
1. Open **System Settings → Bluetooth**.
2. If an old entry for this module is listed (`HC-06` or an older name), click
   **ⓘ → Forget This Device**. macOS remembers old names.
3. Find your sensor's name under **Nearby Devices** and click **Connect**.
   PIN: `1234` (or `0000`).

✅ Look for: your sensor's name under **My Devices**. "Not Connected" is
normal here.

### 8. Allow Terminal to use Bluetooth, and find your sensor
```bash
cd ~/Documents/hc-06-bluetooth-main
.venv/bin/python hc06.py --list
```
If macOS asks to let Terminal use Bluetooth, click **Allow** and run the
command again.

✅ Look for: a line with your sensor's name, like
`98-d3-…  AIIT-07  (not connected)`.

If the command just hangs: **System Settings → Privacy & Security →
Bluetooth → Terminal** on, quit Terminal (`⌘Q`), reopen it, and try again.

### 9. Send your first message
```bash
cd ~/Documents/hc-06-bluetooth-main
.venv/bin/python hc06.py --name AIIT-07 --send "LED ON"
```
✅ Look for: `Connected. The HC-06 LED should now be solid.` and then
`LED is ON`. The LED on pin 3 lights up.

Other commands (use your sensor name):
```bash
.venv/bin/python hc06.py --name AIIT-07 --send "LED OFF"   # LED is OFF
.venv/bin/python hc06.py --name AIIT-07 --send "READ"      # A0 = <number>
.venv/bin/python hc06.py --name AIIT-07                    # chat: type lines, Ctrl+C to quit
.venv/bin/python hc06.py --name AIIT-07 --listen           # only receive
```

---

## Adding your own code

1. Open the sketch in TextEdit:
   ```bash
   cd ~/Documents/hc-06-bluetooth-main
   open -e student/AIIT_Bluetooth/AIIT_Bluetooth.ino
   ```
2. Replace the code (for example with code from Gemini). Keep:
   - `#include "AIITBluetooth.h"` at the top,
   - `bluetoothBegin(SENSOR_NAME);` as the first line of `setup()`,
   - `bluetoothUpdate();` in `loop()`,
   - an `onMessage(String message)` function.

   Use `send("text")` to send a line to the Mac. Don't edit `AIITBluetooth.h`.
3. Save (`⌘S`), then upload again (step 5). If the build fails, the error
   lines above `[FAILED]` say which line of your code is wrong.

---

## Before class: ask IT

On managed Macs these can be blocked. Ask IT to allow them before students start:

- [ ] Terminal can run, and students can use it.
- [ ] Downloads from `astral.sh` and `github.com` (uv, its Python, this project).
- [ ] Downloads from `pypi.org` and `files.pythonhosted.org` (Python packages).
- [ ] Downloads from `platformio.org` and its registry `*.registry.platformio.org`
      (Arduino build tools, step 5).
- [ ] Students can **pair Bluetooth devices** in System Settings.
- [ ] Students can allow **Terminal** under Privacy & Security → Bluetooth.

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
| `uv: command not found` | Use the full path `~/.local/bin/uv`, as in the steps. |
| `curl: (6) Could not resolve host` or a download stalls | No internet, or the school network blocks the site. See [Before class: ask IT](#before-class-ask-it). |
| `No such file or directory: .venv/bin/...` | You're not in the project folder. Run `cd ~/Documents/hc-06-bluetooth-main`. |
| Step 5: no `/dev/cu.usbmodem…` port | Try another USB cable (some only charge) or port. Avoid hubs. |
| Upload times out (`stk500v2_getsync`) | Another USB port or cable. Nothing wired to pins 0/1. Close any open monitor (`Ctrl+C`). |
| Step 6 shows `HC-06 didn't answer AT` | The HC-06 was connected to something when the Mega started, or TX/RX are swapped. Disconnect it, then press the Mega's reset button. |
| Step 6 shows `Rename failed` | Check the name: 1–20 letters, digits, `-` or `_`. |
| Old name still shows in Bluetooth | Forget the device and pair again (step 7). |
| `No paired device named …` | Pair it first (step 7), and type the name exactly as in step 4. |
| `Could not open the RFCOMM channel` | Another Mac or phone is connected to the sensor (only one at a time), or the sensor has no power. |
| `hc06.py` hangs with no output | Terminal needs Bluetooth permission (step 8). |

---

## For teachers

- `student/connect.html` is an experimental Chrome (Web Serial) page for
  talking to a paired sensor without Terminal. It hasn't been tested on
  hardware yet.
- Arduino IDE can open `student/AIIT_Bluetooth/` too (it's the same sketch
  PlatformIO builds; see `platformio.ini`).
- `rename_hc06.py` only works with the old USB passthrough firmware (in Git
  history) and isn't needed: the sketch renames the HC-06 from `SENSOR_NAME`.
