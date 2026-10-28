# Naming sensors (teacher only)

Teachers name each sensor before class. The student starter kit has no
renaming code, so students' sketches never change the name. The HC-06 keeps
the name you give it. Do steps 1–2 of the main README (uv and the venv)
first.

For each sensor:

1. Make sure nothing is connected to the HC-06 over Bluetooth (its LED blinks).
2. Plug its Mega into this Mac by USB.
3. Open `teacher/naming_config.txt`, set `SENSOR_NAME = AIIT-07` (the new
   name), and save (`⌘S`).
4. From the project folder, run:
   ```bash
   .venv/bin/python teacher/name_sensor.py
   ```
   ✅ Look for: `Named the sensor AIIT-07.`, then `[SUCCESS]` from the
   starter upload, then `Done.`
5. Put the name on a label on the sensor. Students copy it into
   `sensor_config.txt`.

Naming a batch? Skip the config and type each name instead:
`.venv/bin/python teacher/name_sensor.py AIIT-08`.

If it says `HC-06 didn't answer AT`: something is connected to the HC-06, or
TX/RX are swapped. Disconnect it and run the command again.

Names: 1–20 letters, digits, `-` or `_`, no spaces. A Mac that already paired
the sensor under an old name must **Forget** it and pair again.
