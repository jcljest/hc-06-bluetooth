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

### 3. Put your sensor's name in the config file
Your sensor's name is on its label. Your teacher set it, so
you don't rename the sensor yourself.

1. In VS Code's file list, open `sensor_config.txt`.
2. Replace `AIIT-YOURNAME` with the name on your label, exactly as written.
3. Save: `⌘S`.

Then check it:
```bash
grep SENSOR_NAME sensor_config.txt
```
✅ Look for: `SENSOR_NAME = AIIT-YOURNAME`, but with **your** sensor's name.

`hc06.py` and `controller.py` read the name from this file, so you never
type it in a command. If you get a different sensor, change the name here.

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

### 5. Check that the sketch is running
```bash
.venv/bin/pio device monitor
```
✅ Look for: `Bluetooth ready.`

Press `Ctrl+C` to leave the monitor.

### 6. Pair the sensor (the only step outside VS Code)
1. Open **System Settings → Bluetooth**.
2. If an old entry for this module is listed (`HC-06` or an older name), click
   **ⓘ → Forget This Device**. macOS remembers old names.
3. Find the name on your label under **Nearby Devices** and click **Connect**.
   PIN: `1234` (or `0000`).

✅ Look for: your sensor's name under **My Devices**. "Not Connected" is
normal here: `hc06.py` and `controller.py` connect when they run. Don't
click **Connect** here again later, because macOS drops that connection
after about 15 seconds.

### 7. Allow VS Code to use Bluetooth, and find your sensor
```bash
.venv/bin/python hc06.py --list
```
If macOS asks to let **Visual Studio Code** use Bluetooth, click **Allow**
and run the command again. If it asks for a PIN, enter `1234` (or `0000`).

✅ Look for: a line with your sensor's name, like
`98-d3-…  AIIT-YOURNAME  (not connected)`, with your sensor's name.

If the command just hangs: **System Settings → Privacy & Security →
Bluetooth → Visual Studio Code** on, quit VS Code (`⌘Q`), reopen the project,
open a new terminal, and try again.

### 8. Send your first message
```bash
.venv/bin/python hc06.py --send "LED ON"
```
✅ Look for: `Connected. The HC-06 LED should now be solid.` and then
`LED is ON`. The LED on pin 3 lights up.

Other commands:
```bash
.venv/bin/python hc06.py --send "LED OFF"   # LED is OFF
.venv/bin/python hc06.py --send "READ"      # A0 = <number>
.venv/bin/python hc06.py                    # chat: type lines, Ctrl+C to quit
.venv/bin/python hc06.py --listen           # only receive
```

### 9. Use the game controller
```bash
.venv/bin/python controller.py
```
A window opens with a D-pad and **K**/**L** buttons. It connects to the
sensor named in `sensor_config.txt` (step 3).

✅ Look for: `Opening the controller for AIIT-YOURNAME` (your sensor's name) in the terminal, then
`Connected. Press a button.` in green in the window. Hold **K**: the window
shows `→ K`, then `← Pin 2 HIGH`. Let go: `→ K RELEASED`, then `← Pin 2 LOW`.

You can click the buttons or use the keys: arrows or `W` `A` `S` `D` for the
D-pad, `K` and `L` for the buttons. Close the window to quit. If the window shows a red message, click
**Reconnect** after fixing it (see [Troubleshooting](#troubleshooting)).

Each button sends one line to your sketch, so `onMessage` decides what it
does:

| You do | Sketch gets |
|---|---|
| Press a button | `UP`, `DOWN`, `LEFT`, `RIGHT`, `K` or `L` |
| Let go of it | `UP RELEASED`, `DOWN RELEASED`, … `L RELEASED` |

The starter sketch: hold **K** = pin 2 HIGH until you let go, **L** = LED off,
**UP** = read A0, hold **DOWN** = LED on until you let go. **LEFT** and **RIGHT** come back as
`I got: …`, ready for your own code.

To see what each button sends without a sensor:
`.venv/bin/python controller.py --demo`.

---

## Writing your own code

You write code in VS Code in the same file, then upload it with the same
command as step 4. Finish steps 1–9 first so you know the sensor works.

### The file you edit

Open `student/AIIT_Bluetooth/AIIT_Bluetooth.ino` in VS Code's file list.
It's the only file you change. Don't edit `AIITBluetooth.h`: it handles
the Bluetooth parts.

Every program needs these four parts:

```cpp
#include "AIITBluetooth.h"      // 1. keep at the top

void setup() {
  bluetoothBegin();             // 2. first line of setup()
  // your setup code
}

void loop() {
  bluetoothUpdate();            // 3. in loop(); checks for messages
  // your code that repeats
}

void onMessage(String message) {  // 4. runs each time the Mac sends a line
  send("I got: " + message);      //    send() sends a line back to the Mac
}
```

Tools you can use:

| Code | What it does |
|---|---|
| `send("text")` | Sends a line to the Mac (shows up in `hc06.py`). |
| `Serial.println("text")` | Prints to the USB monitor only, for checking your code. |
| `message == "GO"` | Checks which message arrived (add `message.toUpperCase();` first to ignore case). |
| `message.startsWith("BLINK ")` / `message.substring(6).toInt()` | Reads a number from a message like `BLINK 5`. |
| `millis()` | Milliseconds since the Mega started. Use it for timing instead of a long `delay()`. |

### Your edit–upload loop

Do these each time you change the code.

**a. Save:** `⌘S`.

**b. Check it compiles (no Mega needed):**
```bash
.venv/bin/pio run
```
✅ Look for: `[SUCCESS]`.

If you see `[FAILED]`, look higher up for a line like
`student/AIIT_Bluetooth/AIIT_Bluetooth.ino:15:1: error: expected ';' before '}' token`.
The `15` is the line number. `⌘`-click that path to jump to the line. Fix
the first error first, because the later errors often come from it.

**c. Upload and watch the log:** plug in the Mega, then run:
```bash
.venv/bin/pio run -t upload -t monitor
```
✅ Look for: `[SUCCESS]`, then `Bluetooth ready.`
Your own `Serial.println` lines show up here too. Press `Ctrl+C` to leave.

**d. Test over Bluetooth:**
```bash
.venv/bin/python hc06.py
```
Type your messages and press Return. Press `Ctrl+C` to quit.
Or test with the controller: `.venv/bin/python controller.py` (step 9).

Close the monitor (`Ctrl+C`) before uploading again. Only one program can
use the USB port at a time.

### Example: stream a sensor reading

This code sends A0 once a second after you send `START`, stops on `STOP`, and
blinks the LED on `BLINK 3`:

```cpp
#include "AIITBluetooth.h"

const int LED_PIN = 3;
bool streaming = false;
unsigned long lastSend = 0;

void setup() {
  bluetoothBegin();  // keep this first
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  bluetoothUpdate();  // keep this

  // Every 1000 ms, without delay(), so messages still get through.
  if (streaming && millis() - lastSend >= 1000) {
    lastSend = millis();
    send("A0 = " + String(analogRead(A0)));
  }
}

void onMessage(String message) {
  message.toUpperCase();
  if (message == "START") {
    streaming = true;
    send("Streaming A0");
  } else if (message == "STOP") {
    streaming = false;
    send("Stopped");
  } else if (message.startsWith("BLINK ")) {
    int times = message.substring(6).toInt();
    for (int i = 0; i < times; i++) {
      digitalWrite(LED_PIN, HIGH);
      delay(200);
      digitalWrite(LED_PIN, LOW);
      delay(200);
    }
    send("Blinked " + String(times));
  } else {
    send("I got: " + message);
  }
}
```

### Rules that keep Bluetooth working

- Keep `bluetoothUpdate();` running often. A long `delay()` in `loop()` makes
  messages wait until the delay ends. Time things with `millis()` as in the
  example.
- Don't use `Serial1`, or pins 18 and 19, for anything else. The HC-06 is
  on them.
- Send short lines. Each `send()` is one line.

### Start over

To get the original starter code back:
```bash
git checkout student/AIIT_Bluetooth/AIIT_Bluetooth.ino
```
To keep your version, copy the file somewhere else first.

VS Code colors `.ino` files as C++ because of the project's
`.vscode/settings.json`. It may still miss some errors. `pio run` is the
real check.

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
| `No sensor name yet` | Put the name from your label in `sensor_config.txt` and save (step 3). |
| Old name still shows in Bluetooth | Forget the device and pair again (step 6). |
| `No paired device named …` | Pair it first (step 6). The name in `sensor_config.txt` must match the label exactly, including capitals and dashes. |
| Connection drops after about 15 seconds | Connect with `hc06.py` or `controller.py`, not the **Connect** button in System Settings. |
| `Could not open the RFCOMM channel` | Another Mac or phone is connected to the sensor (only one at a time), or the sensor has no power. |
| `hc06.py` hangs with no output | VS Code needs Bluetooth permission (step 7). |
| `controller.py`: `No module named tkinter` or the window never opens | The venv uses the wrong Python. Delete it (`rm -rf .venv`) and redo step 2. |

---

## For teachers

- Arduino IDE can open `student/AIIT_Bluetooth/` too (it's the same sketch
  PlatformIO builds; see `platformio.ini`).
- Name and label each sensor before class: see `teacher/README.md`. The
  student starter sketch can't rename sensors.
