# HC-06 Bluetooth ↔ macOS

Talk to an Arduino Mega over an HC-06 Bluetooth module from a MacBook.

These steps assume a **fresh, school-managed MacBook**: no admin password, no
Python or developer tools installed. Each step ends with **You should see**.
If you don't see it, stop and check [Troubleshooting](#troubleshooting).

The HC-06 is Bluetooth Classic, not Bluetooth Low Energy. iPhones and iPads
can't connect to it.

| Path | Who | Needs |
|---|---|---|
| [A. Student setup](#a-student-setup-no-python) | Students | Arduino IDE + Google Chrome |
| [B. Teacher tools](#b-teacher-tools-python) | Teacher | Terminal, Apple's developer tools, Python |
| [Before class: ask IT](#before-class-ask-it) | Teacher → IT | Do this once before students start |

---

## A. Student setup (no Python)

> **Not yet tested on hardware:** step A6 (Chrome talking to the HC-06). If it
> fails, the rest of path A still works; tell your teacher.

### A1. Get the files
1. Your teacher shares a folder called `AIIT_Bluetooth` (it holds
   `AIIT_Bluetooth.ino` and `AIITBluetooth.h`) and a file `connect.html`.
2. Save them to your **Documents** folder. Keep `AIIT_Bluetooth.ino` and
   `AIITBluetooth.h` together in the `AIIT_Bluetooth` folder; the folder
   name has to match the `.ino` file name.

**You should see:** `Documents/AIIT_Bluetooth/` with both files, and
`Documents/connect.html`.

### A2. Install the Arduino IDE
1. Open **Self Service** (your school's app store) and install **Arduino IDE**.
   If it isn't there, ask your teacher.
2. Open Arduino IDE. If macOS asks whether to open an app downloaded from the
   internet, click **Open**.

**You should see:** the Arduino IDE window with an empty sketch.

### A3. Add Mega support (once per Mac)
1. Click the **Boards Manager** icon on the left (it looks like a circuit board).
2. Search `Arduino AVR Boards` and click **Install**.

**You should see:** "Arduino AVR Boards … INSTALLED".

### A4. Name your sensor and upload
1. **File → Open…** → `Documents/AIIT_Bluetooth/AIIT_Bluetooth.ino`.
   You should get two tabs: `AIIT_Bluetooth.ino` and `AIITBluetooth.h`.
   Only edit the first one.
2. Find `const char SENSOR_NAME[] = "AIIT-01";` and change `AIIT-01` to your
   own name: 1–20 letters, digits, `-` or `_`, no spaces (e.g. `AIIT-07`).
3. Plug the Mega into the MacBook with a USB cable.
4. Top bar: **Select Board** → **Arduino Mega or Mega 2560**, on the port
   that appears when you plug in (e.g. `/dev/cu.usbmodem…`).
5. Click **Upload** (the → arrow).
6. **Tools → Serial Monitor**, set the speed (bottom right) to **115200 baud**.

**You should see:** "Done uploading", then in Serial Monitor:
`Sensor name: AIIT-07` and `Bluetooth ready.`

### A5. Pair the sensor with the Mac
1. **System Settings → Bluetooth.**
2. If an old entry for this module is listed (`HC-06` or an older name),
   click **ⓘ → Forget This Device**. macOS remembers old names.
3. Find your sensor's name under **Nearby Devices** and click **Connect**.
   PIN: `1234` (or `0000`).

**You should see:** your sensor listed under **My Devices**. It's normal for
it to say "Not Connected" until the next step.

### A6. Talk to it from Chrome
1. Open `Documents/connect.html` in **Google Chrome** (drag the file onto a
   Chrome window). Safari won't work.
2. Click **Connect to my sensor**, pick your sensor's name, click **Connect**.
3. If macOS asks to let Chrome use Bluetooth, click **Allow**.
4. Click **LED ON**.

**You should see:** "Connected" in green, the HC-06's red light stops
blinking and stays on, and the page shows `Sensor: LED is ON`.

### A7. Add your own code
Paste new code only into `AIIT_Bluetooth.ino`, then upload again (A4 step 5).
Keep `bluetoothBegin(SENSOR_NAME);` in `setup()` and `bluetoothUpdate();` in
`loop()`. Use `send("text")` to send a line to the Mac; `onMessage(message)`
runs every time the Mac sends one.

---

## B. Teacher tools (Python)

`hc06.py` is a Terminal tool for testing. It works on any macOS version
because it opens the Bluetooth link itself through Apple's IOBluetooth
framework. (Recent macOS doesn't start the link when `/dev/cu.<name>` is
opened, so the HC-06 keeps blinking fast with ordinary serial tools.)

### B1. Install Apple's developer tools (once per Mac)
1. Open **Terminal** (Applications → Utilities).
2. Run `xcode-select --install` and click **Install** in the pop-up. This is
   a large download (1–2 GB). If it asks for an admin password, ask IT to
   install "Xcode Command Line Tools" for you.

**You should see:** `python3 --version` prints `Python 3.9` or newer.

### B2. Get the code
```bash
cd ~/Documents
git clone https://github.com/jcljest/hc-06-bluetooth.git
cd hc-06-bluetooth
```
**You should see:** `ls` lists `hc06.py`, `README.md`, `student`.

### B3. Set up Python (once)
Run these one at a time from the `hc-06-bluetooth` folder:
```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```
`.venv` is a private Python folder for this project, so nothing is installed
system-wide and no admin password is needed.

**You should see:** the last command ends with `Successfully installed …`.

### B4. Allow Bluetooth for Terminal
1. Run `.venv/bin/python hc06.py --list`.
2. When macOS asks, allow Terminal to use Bluetooth. If no prompt appears:
   **System Settings → Privacy & Security → Bluetooth → Terminal** on, then
   run the command again.

**You should see:** a list of paired devices including your sensor's name.
If the command just hangs, Terminal doesn't have Bluetooth permission yet.

### B5. Send a test message
```bash
.venv/bin/python hc06.py --name AIIT-07 --send "LED ON"
```
**You should see:** `LED is ON`, and the LED on pin 3 lights.

Other uses:
```bash
.venv/bin/python hc06.py --name AIIT-07            # type lines, see replies
.venv/bin/python hc06.py --name AIIT-07 --listen   # receive only
```
Options: `--address`, `--channel`, `--eol lf|crlf|none`, `--wait SECONDS`.

### B6. Optional: PlatformIO instead of Arduino IDE
`src/main.cpp` is an exact copy of `student/AIIT_Bluetooth/AIIT_Bluetooth.ino`
and uses the same `AIITBluetooth.h` (see `platformio.ini`). Keep them
identical; `python3 scripts/check_sketch_sync.py` checks.
```bash
.venv/bin/pio run -t upload      # build + flash (first run downloads ~150 MB)
.venv/bin/pio device monitor     # USB log at 115200
```

---

## Before class: ask IT

On managed Macs, any of these can be blocked by policy. Ask IT to confirm or
allow them before students start:

- [ ] **Arduino IDE** available in Self Service (or installable without admin).
- [ ] Downloads from `downloads.arduino.cc` allowed (A3 needs them).
- [ ] Students can **pair Bluetooth devices** in System Settings.
- [ ] **Google Chrome** installed, and the Chrome policy for serial ports
      ("Web Serial", `DefaultSerialGuardSetting`) not set to block.
- [ ] Chrome allowed to use Bluetooth (Privacy & Security → Bluetooth).
- [ ] Teacher Mac only: Xcode Command Line Tools installed (B1).

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
| Serial Monitor shows `HC-06 didn't answer AT` | Something was connected to the HC-06 when the Mega started, or TX/RX are swapped. Disconnect it in Chrome/Bluetooth, then press the Mega's reset button. |
| Serial Monitor shows `Rename failed` | Check the name: 1–20 letters, digits, `-` or `_`. |
| Old name still shows on the Mac | Forget the device in Bluetooth settings and pair again (A5). |
| Upload times out (`stk500v2_getsync`) | Try another USB cable or port (avoid hubs). Make sure nothing is wired to pins 0/1. Check the board and port in the top bar. |
| No port appears when the Mega is plugged in | Try a different cable; some are charge-only. |
| Chrome's list is empty | Pair the sensor first (A5). Then try **Show all ports** on the page. |
| Chrome connects but the HC-06 keeps blinking fast / nothing comes back | Chrome may not be able to start the Bluetooth link on this macOS version. Tell your teacher. |
| Only one Mac can talk to the sensor | Normal: the HC-06 takes one connection at a time. Disconnect the other device. |
| `hc06.py` hangs with no output | Terminal needs Bluetooth permission (B4). |

`rename_hc06.py` only works with the old USB passthrough firmware (Git history
before the student kit) and isn't needed anymore: the sketch renames the
HC-06 itself from `SENSOR_NAME`.
