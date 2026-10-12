#!/usr/bin/env python3
"""Rename an HC-06 through the Arduino Mega it is wired to (USB cable).

The HC-06 only accepts AT commands on its wired serial pins, and only while
nothing is connected over Bluetooth (LED blinking). The Mega firmware in
src/main.cpp forwards USB Serial to the HC-06 and logs its replies as
"HC06> <reply>", so this script talks to the HC-06 through the Mega.

Usage:
    python rename_hc06.py --check           # confirm the HC-06 answers AT
    python rename_hc06.py AIIT-01           # rename it
    python rename_hc06.py AIIT-01 --port /dev/cu.usbmodem1101

After renaming, remove the old "HC-06" entry in System Settings > Bluetooth
and pair again: macOS keeps showing the cached old name otherwise.
"""

import argparse
import glob
import re
import sys
import time

try:
    import serial
except ImportError:
    sys.exit("pyserial is missing. Run: pip install -r requirements.txt")

USB_BAUD = 115200
MAX_NAME = 20


def find_port():
    ports = sorted(glob.glob("/dev/cu.usbmodem*") + glob.glob("/dev/cu.usbserial*"))
    return ports[0] if ports else None


def read_for(ser, seconds):
    """Collect everything the Mega prints for a while."""
    end = time.time() + seconds
    buf = b""
    while time.time() < end:
        buf += ser.read(256)
    return buf.decode("utf-8", errors="replace")


def at(ser, command, wait=1.5):
    """Send an AT command (no line ending) and return the HC-06's replies."""
    ser.reset_input_buffer()
    ser.write(command.encode("ascii"))
    out = read_for(ser, wait)
    return " ".join(re.findall(r"HC06> (.*)", out)).strip()


def main():
    ap = argparse.ArgumentParser(description="Rename an HC-06 via the Arduino Mega")
    ap.add_argument("name", nargs="?", help=f"new name, up to {MAX_NAME} characters")
    ap.add_argument("--port", help="Mega USB port (default: auto-detect)")
    ap.add_argument("--check", action="store_true", help="only check that AT works")
    args = ap.parse_args()

    if not args.check and not args.name:
        ap.error("give a new name, or --check")
    if args.name and not re.fullmatch(r"[A-Za-z0-9_-]{1,%d}" % MAX_NAME, args.name):
        ap.error(f"name must be 1-{MAX_NAME} letters, digits, - or _")

    port = args.port or find_port()
    if not port:
        sys.exit("No Arduino USB port found. Plug in the Mega or pass --port.")

    ser = serial.Serial(port, USB_BAUD, timeout=0.1)
    print(f"Opened {port}; waiting for the Mega to restart...")
    banner = read_for(ser, 3)
    if "ready" not in banner:
        sys.exit("The Mega didn't print its ready message. Is the HC-06 firmware "
                 "uploaded? (pio run -t upload)")

    reply = at(ser, "AT")
    if "OK" not in reply:
        sys.exit("The HC-06 didn't answer AT. Disconnect it from every Bluetooth "
                 "device (its LED must be blinking) and check the TX/RX wiring.")
    version = at(ser, "AT+VERSION")
    print(f"HC-06 answers AT. Firmware: {version or 'unknown'}")
    if args.check:
        return

    # Older HC-06 firmware: AT+NAMExxx, no line ending, replies "OKsetname".
    reply = at(ser, "AT+NAME" + args.name)
    if "OK" not in reply:
        # Newer firmware: AT+NAME=xxx with CRLF.
        reply = at(ser, f"AT+NAME={args.name}\r\n")
    if "OK" not in reply:
        sys.exit(f"Rename failed; the HC-06 replied: {reply or 'nothing'}")

    print(f"Renamed to {args.name} (HC-06 replied: {reply}).")
    print("Now: System Settings > Bluetooth > old HC-06 entry > Forget, then pair "
          f"with {args.name} (PIN 1234).")
    print(f"Connect with: python hc06.py --name {args.name}")


if __name__ == "__main__":
    main()
