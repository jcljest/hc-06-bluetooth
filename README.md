# HC-06 Bluetooth ↔ macOS

Python terminal for an HC-06 (Bluetooth Classic / SPP, **not** BLE).

Recent macOS versions don't start the Bluetooth link when `/dev/cu.HC-06` is
opened, so the module keeps blinking fast. `hc06.py` opens the RFCOMM channel
itself through Apple's IOBluetooth framework (via PyObjC). The LED turns solid
while connected.

## Setup (once)
1. Power the HC-06 and pair it in System Settings → Bluetooth (PIN `1234` or `0000`).
2. `python3 -m venv .venv && .venv/bin/pip install --upgrade pip && .venv/bin/pip install -r requirements.txt`
3. Run the script from **Terminal**. When macOS asks, allow Bluetooth access
   (System Settings → Privacy & Security → Bluetooth → Terminal on).
   Without this permission the script hangs silently at the first Bluetooth call.

## Use
```
.venv/bin/python hc06.py                  # interactive: type lines, see replies
.venv/bin/python hc06.py --send "LED ON"  # send one line, print reply, exit
.venv/bin/python hc06.py --listen         # receive only
.venv/bin/python hc06.py --list           # paired devices + connection state
```
Options: `--name` (default `HC-06`), `--address`, `--channel`, `--eol lf|crlf|none`, `--wait SECONDS`.

## Notes
- The HC-06 accepts one connection at a time. Disconnect any phone using it first.
- Baud rate is between the HC-06 and the microcontroller only (default 9600);
  the board's `Serial.begin()` must match. It doesn't matter on the Mac side.
- HC-06 TX → board RX, HC-06 RX ← board TX. HC-06 RX is 3.3 V logic: use a
  voltage divider from a 5 V board's TX.

## Arduino Mega firmware (PlatformIO)
`src/main.cpp` runs the LED commands below; any other Bluetooth line is echoed
back uppercased as `Mega got: <LINE>`. Every line is logged as `BT> <line>` to
USB Serial (115200). HC-06 is on Serial1: TXD → pin 19,
RXD ← pin 18 (via voltage divider), VCC → 5V, GND → GND.

```
.venv/bin/pio run -t upload          # build + flash the Mega
.venv/bin/pio device monitor         # watch the Mega's USB log
```
If upload times out (`stk500v2_getsync`), try a different USB port/cable
(the hub caused this once) and make sure nothing is on pins 0/1.

Round-trip check: `.venv/bin/python hc06.py --send hello` should print
`Mega got: HELLO`.

## LED on pin 3
Wire: pin 3 → 220–330 Ω resistor → LED long leg (anode); short leg → GND.
Commands (case-insensitive): `LED ON`, `LED OFF`, `LED TOGGLE`, `LED` (status).
```
.venv/bin/python hc06.py --send "LED ON"
.venv/bin/python hc06.py --send "LED OFF"
```

## Renaming a module (classroom sets)
The HC-06 takes AT commands on its wired pins only while nothing is connected
over Bluetooth (LED blinking). With the Mega firmware uploaded and USB plugged in:
```
python rename_hc06.py --check     # confirm the HC-06 answers AT
python rename_hc06.py AIIT-01     # rename (1-20 letters, digits, - or _)
```
Then in System Settings → Bluetooth, **Forget** the old entry and pair again
(macOS caches names). Connect with `python hc06.py --name AIIT-01`.
