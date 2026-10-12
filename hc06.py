#!/usr/bin/env python3
"""Connect to an HC-06 (Bluetooth Classic / SPP, not BLE) from macOS and talk to it.

Recent macOS versions do not bring up the Bluetooth link when /dev/cu.HC-06 is
opened, so the module keeps blinking fast. This script opens the RFCOMM
channel itself through Apple's IOBluetooth framework. While it is connected,
the HC-06 LED turns solid.

One-time setup:
  1. Pair the HC-06 in System Settings > Bluetooth (PIN 1234 or 0000).
  2. Run this script from Terminal, and allow Terminal under
     System Settings > Privacy & Security > Bluetooth when asked.

Usage:
    python hc06.py                      # interactive: type lines, see replies
    python hc06.py --send "LED ON"      # send one line, print any reply, exit
    python hc06.py --listen             # only print what the module sends
    python hc06.py --list               # list paired Bluetooth devices
    python hc06.py --name MyBT          # module renamed with AT+NAME
    python hc06.py --address 20-16-06-30-31-23
"""

import argparse
import queue
import sys
import threading
import time

try:
    import IOBluetooth
    import objc
    from Foundation import NSDate, NSDefaultRunLoopMode, NSObject, NSRunLoop
except ImportError:
    sys.exit("PyObjC is missing. Run: pip install -r requirements.txt")

DEFAULT_NAME = "HC-06"
DEFAULT_CHANNEL = 1  # HC-06 serves SPP on RFCOMM channel 1
kIOReturnSuccess = 0


def pump(seconds):
    """Run the macOS run loop so IOBluetooth can deliver callbacks."""
    NSRunLoop.currentRunLoop().runMode_beforeDate_(
        NSDefaultRunLoopMode, NSDate.dateWithTimeIntervalSinceNow_(seconds))


class ChannelDelegate(NSObject):
    """Receives data and close events from the RFCOMM channel."""

    def init(self):
        self = objc.super(ChannelDelegate, self).init()
        self.closed = False
        return self

    def rfcommChannelData_data_length_(self, channel, data, length):
        if not isinstance(data, (bytes, bytearray)):
            data = bytes(data.as_buffer(length))
        sys.stdout.write(bytes(data[:length]).decode("utf-8", errors="replace"))
        sys.stdout.flush()

    def rfcommChannelClosed_(self, channel):
        self.closed = True


def paired_devices():
    return list(IOBluetooth.IOBluetoothDevice.pairedDevices() or [])


def find_device(name, address):
    if address:
        return IOBluetooth.IOBluetoothDevice.deviceWithAddressString_(address)
    for dev in paired_devices():
        if (dev.name() or "").lower() == name.lower():
            return dev
    return None


def find_spp_channel(dev):
    """Read the SPP channel from the cached SDP record, else use channel 1."""
    for svc in dev.services() or []:
        result = svc.getRFCOMMChannelID_(None)
        # Without out-param metadata PyObjC returns only the status int.
        if isinstance(result, tuple) and result[0] == kIOReturnSuccess:
            return result[1]
    return DEFAULT_CHANNEL


def connect(dev, channel_id):
    print(f"Connecting to {dev.name()} ({dev.addressString()}), "
          f"RFCOMM channel {channel_id}...", file=sys.stderr)
    delegate = ChannelDelegate.alloc().init()
    status, channel = dev.openRFCOMMChannelSync_withChannelID_delegate_(
        None, channel_id, delegate)
    if status != kIOReturnSuccess or channel is None:
        sys.exit(
            f"Could not open the RFCOMM channel (IOReturn {status:#x}).\n"
            "Check that the HC-06 is powered, in range, and not connected to "
            "another device (phone, other computer)."
        )
    print("Connected. The HC-06 LED should now be solid.", file=sys.stderr)
    return channel, delegate


def send_line(channel, text, eol):
    data = (text + eol).encode("utf-8")
    mtu = channel.getMTU() or 127
    for i in range(0, len(data), mtu):
        chunk = data[i:i + mtu]
        status = channel.writeSync_length_(chunk, len(chunk))
        if status != kIOReturnSuccess:
            print(f"[write failed: IOReturn {status:#x}]", file=sys.stderr)
            return


def stdin_reader(lines):
    """Read stdin on a background thread; the main thread owns Bluetooth."""
    for line in sys.stdin:
        lines.put(line.rstrip("\r\n"))
    lines.put(None)  # EOF


def main():
    ap = argparse.ArgumentParser(description="HC-06 Bluetooth Classic terminal for macOS")
    ap.add_argument("--name", default=DEFAULT_NAME,
                    help=f"paired device name (default {DEFAULT_NAME})")
    ap.add_argument("--address", help="device address, e.g. 20-16-06-30-31-23")
    ap.add_argument("--channel", type=int, help="RFCOMM channel (default: from SDP, else 1)")
    ap.add_argument("--send", metavar="TEXT", help="send one line and exit")
    ap.add_argument("--wait", type=float, default=1.0,
                    help="seconds to wait for a reply after --send (default 1)")
    ap.add_argument("--listen", action="store_true", help="receive only")
    ap.add_argument("--eol", choices=["lf", "crlf", "none"], default="lf",
                    help="line ending appended to sent text (default lf)")
    ap.add_argument("--list", action="store_true", help="list paired devices and exit")
    args = ap.parse_args()

    if args.list:
        for dev in paired_devices():
            state = "connected" if dev.isConnected() else "not connected"
            print(f"{dev.addressString()}  {dev.name()}  ({state})")
        return

    dev = find_device(args.name, args.address)
    if dev is None:
        sys.exit(f"No paired device named {args.name!r}. Pair it in System Settings > "
                 "Bluetooth (PIN 1234 or 0000), or pass --address. Use --list to see "
                 "paired devices.")
    if not dev.isPaired():
        sys.exit(f"{dev.name() or dev.addressString()} is not paired. Pair it in "
                 "System Settings > Bluetooth (PIN 1234 or 0000) first.")

    eol = {"lf": "\n", "crlf": "\r\n", "none": ""}[args.eol]
    channel, delegate = connect(dev, args.channel or find_spp_channel(dev))

    try:
        if args.send is not None:
            send_line(channel, args.send, eol)
            end = time.time() + args.wait
            while time.time() < end and not delegate.closed:
                pump(0.05)
        else:
            lines = queue.Queue()
            if args.listen:
                print("Listening. Ctrl-C to quit.", file=sys.stderr)
            else:
                print("Type a line and press Enter to send. Ctrl-C or Ctrl-D to quit.",
                      file=sys.stderr)
                threading.Thread(target=stdin_reader, args=(lines,), daemon=True).start()
            while not delegate.closed:
                pump(0.05)
                try:
                    line = lines.get_nowait()
                except queue.Empty:
                    continue
                if line is None:
                    break
                send_line(channel, line, eol)
            if delegate.closed:
                print("\n[connection closed by the module]", file=sys.stderr)
    except KeyboardInterrupt:
        pass
    finally:
        channel.closeChannel()
        dev.closeConnection()
        print("\nDisconnected.", file=sys.stderr)


if __name__ == "__main__":
    main()
