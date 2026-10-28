#!/usr/bin/env python3
"""A game-controller window for the HC-06 sensor: a D-pad and K/L buttons.

Each button sends one text line to the sensor, so the Arduino sketch decides
what it does in onMessage():

    pressed:   UP  DOWN  LEFT  RIGHT  K  L
    let go:    UP RELEASED  ...  L RELEASED

Click the buttons, or use the keyboard: arrow keys or WASD for the D-pad, K and L.
Lines the sensor sends back show up in the window.

Usage:
    .venv/bin/python controller.py                    # name from sensor_config.txt
    .venv/bin/python controller.py --name AIIT-YOURNAME
    .venv/bin/python controller.py --demo             # no Bluetooth, just show messages
"""

import argparse
import sys
import time
import tkinter as tk

import hc06
import objc
from Foundation import NSObject

KEYS = {"Up": "UP", "Down": "DOWN", "Left": "LEFT", "Right": "RIGHT",
        "w": "UP", "s": "DOWN", "a": "LEFT", "d": "RIGHT", "k": "K", "l": "L"}
KEYS.update({key.upper(): button for key, button in KEYS.items() if len(key) == 1})  # caps lock / shift
RELEASE_DELAY_MS = 40  # ignore key auto-repeat (release + press in quick pairs)

BODY, BODY_EDGE = "#3b3f4a", "#2a2d35"
PAD, PAD_DOWN = "#1f2128", "#5a8dee"
K_COLOR, L_COLOR, BTN_DOWN = "#d64545", "#e0a526", "#ffffff"
LABEL = "#f2f2f2"


class ControllerDelegate(NSObject):
    """Collects what the sensor sends and notices when the link closes."""

    def init(self):
        self = objc.super(ControllerDelegate, self).init()
        self.closed = False
        self.received = ""
        return self

    def rfcommChannelData_data_length_(self, channel, data, length):
        if not isinstance(data, (bytes, bytearray)):
            data = bytes(data.as_buffer(length))
        self.received += bytes(data[:length]).decode("utf-8", errors="replace")

    def rfcommChannelClosed_(self, channel):
        self.closed = True


class Link:
    """The Bluetooth connection to one paired sensor."""

    def __init__(self, name, address, channel_id):
        self.name, self.address, self.channel_id = name, address, channel_id
        self.dev = self.channel = self.delegate = None
        self.last_sent = 0.0

    def open(self):
        """Connect. Returns an error message, or None when connected."""
        self.dev = hc06.find_device(self.name, self.address)
        if self.dev is None:
            return (f"No paired device named {self.name}. Pair it in System "
                    "Settings > Bluetooth (PIN 1234), then click Reconnect.")
        self.delegate = ControllerDelegate.alloc().init()
        status, self.channel = self.dev.openRFCOMMChannelSync_withChannelID_delegate_(
            None, self.channel_id or hc06.find_spp_channel(self.dev), self.delegate)
        if status != hc06.kIOReturnSuccess or self.channel is None:
            self.channel = None
            return ("Could not connect. Is the sensor powered, and not connected "
                    "to another Mac?")
        self.last_sent = time.time()
        return None

    @property
    def connected(self):
        return self.channel is not None and not self.delegate.closed

    def send(self, text):
        if self.connected:
            hc06.send_line(self.channel, text, "\n")
            self.last_sent = time.time()

    def poll(self):
        """Let macOS deliver Bluetooth events; return the complete lines received."""
        hc06.pump(0)
        if self.connected and time.time() - self.last_sent >= hc06.KEEPALIVE_SECONDS:
            self.send("")  # blank line keeps the link out of sniff mode; see hc06.py
        if self.delegate is None:
            return []
        *lines, self.delegate.received = self.delegate.received.replace("\r", "").split("\n")
        return [line for line in lines if line.strip()]

    def close(self):
        if self.channel is not None:
            self.channel.closeChannel()
            self.channel = None
        if self.dev is not None:
            self.dev.closeConnection()


class DemoLink:
    """Stands in for the sensor with --demo: nothing is sent anywhere."""
    connected = True

    def open(self):
        return None

    def send(self, text):
        pass

    def poll(self):
        return []

    def close(self):
        pass


class Controller:
    def __init__(self, root, link, title):
        self.root, self.link = root, link
        self.held = set()          # buttons currently pressed
        self.pending_release = {}  # button -> after() id
        self.shapes = {}           # button -> (canvas items to recolor, normal color, pressed color)

        root.title(title)
        root.resizable(False, False)
        root.configure(bg=BODY_EDGE)

        self.canvas = tk.Canvas(root, width=520, height=260, bg=BODY_EDGE,
                                highlightthickness=0)
        self.canvas.pack(padx=12, pady=(12, 6))
        self.draw()

        self.status = tk.Label(root, text="", bg=BODY_EDGE, fg=LABEL, anchor="w")
        self.status.pack(fill="x", padx=14)
        self.reconnect_btn = tk.Button(root, text="Reconnect", command=self.connect)

        self.log = tk.Text(root, height=8, width=60, bg=PAD, fg=LABEL,
                           insertbackground=LABEL, relief="flat", state="disabled",
                           font=("Menlo", 12))
        self.log.pack(fill="both", padx=12, pady=(6, 4))
        tk.Label(root, text="Keys: arrows or WASD = D-pad, K, L",
                 bg=BODY_EDGE, fg="#a0a4ad").pack(pady=(0, 10))

        root.bind("<KeyPress>", self.key_down)
        root.bind("<KeyRelease>", self.key_up)
        root.bind("<FocusOut>", lambda e: self.release_all())
        root.protocol("WM_DELETE_WINDOW", self.quit)

        root.after(100, self.connect)
        root.after(20, self.poll)

    # ---- drawing ----

    def draw(self):
        c = self.canvas
        c.create_oval(10, 30, 210, 250, fill=BODY, outline="")
        c.create_oval(310, 30, 510, 250, fill=BODY, outline="")
        c.create_rectangle(110, 30, 410, 250, fill=BODY, outline="")

        cx, cy, arm, w = 110, 140, 62, 40  # D-pad center, arm length, arm width
        c.create_rectangle(cx - w / 2, cy - w / 2, cx + w / 2, cy + w / 2, fill=PAD, outline="")
        arms = {
            "UP": (cx - w / 2, cy - arm, cx + w / 2, cy - w / 2, "▲"),
            "DOWN": (cx - w / 2, cy + w / 2, cx + w / 2, cy + arm, "▼"),
            "LEFT": (cx - arm, cy - w / 2, cx - w / 2, cy + w / 2, "◀"),
            "RIGHT": (cx + w / 2, cy - w / 2, cx + arm, cy + w / 2, "▶"),
        }
        for button, (x1, y1, x2, y2, arrow) in arms.items():
            rect = c.create_rectangle(x1, y1, x2, y2, fill=PAD, outline="")
            text = c.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=arrow,
                                 fill="#6f7480", font=("Helvetica", 14))
            self.add_button(button, [rect], PAD, PAD_DOWN, [rect, text])

        for button, x, y, color in (("K", 370, 160, K_COLOR), ("L", 440, 120, L_COLOR)):
            r = 30
            oval = c.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")
            text = c.create_text(x, y, text=button, fill=LABEL,
                                 font=("Helvetica", 20, "bold"))
            self.add_button(button, [oval], color, BTN_DOWN, [oval, text])

    def add_button(self, button, fill_items, normal, pressed, click_items):
        self.shapes[button] = (fill_items, normal, pressed)
        for item in click_items:
            self.canvas.tag_bind(item, "<ButtonPress-1>", lambda e, b=button: self.press(b))
            self.canvas.tag_bind(item, "<ButtonRelease-1>", lambda e, b=button: self.release(b))

    def show_pressed(self, button, down):
        items, normal, pressed = self.shapes[button]
        for item in items:
            self.canvas.itemconfigure(item, fill=pressed if down else normal)

    # ---- buttons ----

    def press(self, button):
        if button in self.pending_release:  # key auto-repeat: still held
            self.root.after_cancel(self.pending_release.pop(button))
            return
        if button in self.held:
            return
        self.held.add(button)
        self.show_pressed(button, True)
        self.send(button)

    def release(self, button):
        self.pending_release.pop(button, None)
        if button not in self.held:
            return
        self.held.discard(button)
        self.show_pressed(button, False)
        self.send(button + " RELEASED")

    def release_all(self):
        for button in list(self.held):
            self.release(button)

    def key_down(self, event):
        button = KEYS.get(event.keysym)
        if button:
            self.press(button)

    def key_up(self, event):
        button = KEYS.get(event.keysym)
        if button and button in self.held and button not in self.pending_release:
            self.pending_release[button] = self.root.after(
                RELEASE_DELAY_MS, lambda: self.release(button))

    # ---- Bluetooth ----

    def send(self, text):
        if self.link.connected:
            self.link.send(text)
            self.write("→ " + text)
        else:
            self.write("(not connected) " + text)

    def write(self, line):
        self.log.configure(state="normal")
        self.log.insert("end", line + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def set_status(self, text, ok):
        self.status.configure(text=text, fg="#6fd38a" if ok else "#ff8a80")
        if ok:
            self.reconnect_btn.pack_forget()
        else:
            self.reconnect_btn.pack(before=self.log, padx=12, anchor="w")

    def connect(self):
        self.set_status("Connecting...", True)
        self.root.update_idletasks()
        error = self.link.open()
        if error:
            self.set_status(error, False)
        else:
            self.set_status("Connected. Press a button.", True)

    def poll(self):
        was_connected = self.link.connected
        for line in self.link.poll():
            self.write("← " + line)
        if was_connected and not self.link.connected:
            self.link.close()
            self.set_status("Connection closed by the sensor.", False)
        self.root.after(20, self.poll)

    def quit(self):
        self.link.close()
        self.root.destroy()


def main():
    ap = argparse.ArgumentParser(description="Game-controller window for an HC-06 sensor")
    ap.add_argument("--name", help="paired sensor name (default: SENSOR_NAME in sensor_config.txt)")
    ap.add_argument("--address", help="device address, e.g. 20-16-06-30-31-23")
    ap.add_argument("--channel", type=int, help="RFCOMM channel (default: from SDP, else 1)")
    ap.add_argument("--demo", action="store_true",
                    help="no Bluetooth: only show the messages each button would send")
    args = ap.parse_args()

    if args.demo:
        link, title = DemoLink(), "Controller (demo, not connected)"
    else:
        name = args.name or hc06.configured_name()
        if name is None and not args.address:
            sys.exit(hc06.NO_NAME_MESSAGE)
        name = name or args.address
        link, title = Link(name, args.address, args.channel), f"Controller: {name}"
        print(f"Opening the controller for {name}. Close its window to quit.",
              file=sys.stderr)

    root = tk.Tk()
    Controller(root, link, title)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        link.close()


if __name__ == "__main__":
    main()
