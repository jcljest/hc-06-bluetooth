#!/usr/bin/env python3
"""Check that the Arduino IDE sketch and the PlatformIO firmware match.

student/AIIT_Bluetooth/AIIT_Bluetooth.ino (Arduino IDE) and src/main.cpp
(PlatformIO) must be identical. Both include the same
student/AIIT_Bluetooth/AIITBluetooth.h, so that file never needs copying.

Run by hand:   python3 scripts/check_sketch_sync.py
As a Claude Code PostToolUse hook it reads the hook JSON on stdin, stays
quiet unless one of the pair was edited, and exits 2 (message to Claude)
when the two files differ.
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
INO = ROOT / "student" / "AIIT_Bluetooth" / "AIIT_Bluetooth.ino"
CPP = ROOT / "src" / "main.cpp"


def edited_path():
    """Return the file the hook says was edited, or None when run by hand."""
    if sys.stdin.isatty():
        return None
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return None
    path = (data.get("tool_input") or {}).get("file_path")
    return pathlib.Path(path).resolve() if path else None


def main():
    hook_mode = not sys.stdin.isatty()
    edited = edited_path()
    if hook_mode and edited not in (INO.resolve(), CPP.resolve()):
        return 0

    if INO.read_bytes() == CPP.read_bytes():
        if not hook_mode:
            print("In sync: AIIT_Bluetooth.ino and src/main.cpp match.")
        return 0

    other = CPP if edited == INO.resolve() else INO
    print(
        "Arduino IDE sketch and PlatformIO firmware are out of sync.\n"
        f"  {INO.relative_to(ROOT)}\n  {CPP.relative_to(ROOT)}\n"
        f"Apply the same change to {other.relative_to(ROOT)} so the two files "
        "are identical (see CLAUDE.md).",
        file=sys.stderr,
    )
    return 2 if hook_mode else 1


if __name__ == "__main__":
    sys.exit(main())
