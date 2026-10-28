#!/usr/bin/env python3
"""Name one HC-06 sensor, then put the student starter sketch back on its Mega.

Put the name in teacher/naming_config.txt (SENSOR_NAME = AIIT-07) and save.
Plug the sensor's Mega in by USB (nothing connected to the HC-06 over
Bluetooth), then from the project folder:

    .venv/bin/python teacher/name_sensor.py
    .venv/bin/python teacher/name_sensor.py AIIT-07          # override the config
    .venv/bin/python teacher/name_sensor.py --port /dev/cu.usbmodem1101
    .venv/bin/python teacher/name_sensor.py --no-starter

It uploads teacher/name_sensor/ with the name, reads the Mega's log to check
the HC-06 said OK, then uploads student/AIIT_Bluetooth/ again.
"""

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

import serial
from serial.tools import list_ports

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import hc06  # noqa: E402  (shared config reader)

CONFIG = ROOT / "teacher" / "naming_config.txt"
PIO = ROOT / ".venv" / "bin" / "pio"
NAMER = ROOT / "teacher" / "name_sensor"
NAME_RE = re.compile(r"^[A-Za-z0-9_-]{1,20}$")
LOG_SECONDS = 10


def find_port():
    ports = [p.device for p in list_ports.comports() if "usbmodem" in p.device]
    if len(ports) != 1:
        sys.exit(f"Found {len(ports)} Mega ports ({', '.join(ports) or 'none'}). "
                 "Plug in exactly one, or pass --port.")
    return ports[0]


def upload(project_dir, port):
    cmd = [str(PIO), "run", "-d", str(project_dir), "-t", "upload", "--upload-port", port]
    if subprocess.run(cmd).returncode != 0:
        sys.exit(f"Upload failed ({project_dir.name}). See the PlatformIO output above.")


def check_log(lines, name):
    """Return (ok, message) from the naming sketch's log lines."""
    for line in lines:
        if line == f"Sensor name: {name}":
            return True, f"Named the sensor {name}."
        if line.startswith("HC-06 didn't answer AT") or line.startswith("Rename failed"):
            return False, line
    return False, "No answer from the naming sketch. Check the USB cable and wiring."


def read_log(port):
    """Opening the port resets the Mega, so this reads the naming run from the start."""
    lines = []
    with serial.Serial(port, 115200, timeout=0.5) as ser:
        end = time.time() + LOG_SECONDS
        while time.time() < end:
            line = ser.readline().decode("utf-8", errors="replace").strip()
            if line:
                print("  Mega>", line)
                lines.append(line)
                if line.startswith(("Sensor name:", "HC-06 didn't", "Rename failed")):
                    break
    return lines


def main():
    ap = argparse.ArgumentParser(description="Name one HC-06 sensor (teacher tool)")
    ap.add_argument("name", nargs="?",
                    help="new Bluetooth name (default: SENSOR_NAME in teacher/naming_config.txt)")
    ap.add_argument("--port", help="Mega's USB port (default: the only /dev/cu.usbmodem*)")
    ap.add_argument("--no-starter", action="store_true",
                    help="leave the naming sketch on the Mega")
    args = ap.parse_args()

    args.name = args.name or hc06.configured_name(CONFIG)
    if args.name is None:
        sys.exit("No name yet. Open teacher/naming_config.txt, replace "
                 f"{hc06.PLACEHOLDER_NAME} with the sensor's new name, and save (Cmd-S).")
    if not NAME_RE.match(args.name):
        sys.exit("Name must be 1-20 letters, digits, - or _ (no spaces).")
    port = args.port or find_port()

    (NAMER / "sensor_name.h").write_text(f'#define SENSOR_NAME "{args.name}"\n')
    print(f"Naming the sensor on {port} {args.name}...")
    upload(NAMER, port)
    ok, message = check_log(read_log(port), args.name)
    print(message)
    if not ok:
        sys.exit("Not renamed. Disconnect anything using the HC-06 over Bluetooth, "
                 "then run this again.")

    if not args.no_starter:
        print("Putting the student starter sketch back...")
        upload(ROOT, port)

    print(f"\nDone. Label this sensor {args.name}. Macs that paired it under an old "
          "name must Forget it and pair again.")


if __name__ == "__main__":
    main()
