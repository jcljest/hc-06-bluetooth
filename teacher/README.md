# Naming sensors (teacher only)

Teachers name each sensor before class. The student starter kit has no
renaming code, so students' sketches never change the name. The HC-06 keeps
the name you give it.

These steps start **after you've cloned this repository in VS Code** and
opened it. Run every command in VS Code's terminal (**Terminal → New
Terminal**), which opens in the project folder. Copy the whole grey box,
paste it, press Return, then find the text under **✅ Look for**.

---

## Setup (once per Mac)

### 0. Check you're in the project folder
```bash
ls
```
✅ Look for: `hc06.py`, `README.md` and `teacher` in the list.

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
.venv/bin/python -c "import serial; print('USB serial library OK')"
```
✅ Look for: `Creating virtual environment at: .venv`, then
`Installed … packages` (or `Checked … packages` if you've run it before),
then `USB serial library OK`.

The venv is a private Python inside the project folder, so nothing needs an
admin password. If it ever breaks, delete it with `rm -rf .venv` and repeat
this step. If you already did steps 1–2 of the main README on this Mac, skip
to [Name a sensor](#name-a-sensor).

The first sensor you name downloads the Arduino build tools (about 300 MB)
and takes a few minutes. After that each sensor takes under a minute.

Network sites these steps need (ask IT if they're blocked): `astral.sh`,
`github.com`, `pypi.org`, `files.pythonhosted.org`, `platformio.org` and
`*.registry.platformio.org`.

---

## Name a sensor

For each sensor:

1. Make sure nothing is connected to the HC-06 over Bluetooth (its LED blinks).
2. Plug its Mega into this Mac by USB. Only one Mega at a time.
3. Open `teacher/naming_config.txt`, replace `AIIT-YOURNAME` with the new
   name, and save (`⌘S`).
4. Run:
   ```bash
   .venv/bin/python teacher/name_sensor.py
   ```
   ✅ Look for: `Named the sensor AIIT-YOURNAME.` (with the new name), then
   `[SUCCESS]` from the starter upload, then `Done.`
5. Put the name on a label on the sensor. Students copy it into
   `sensor_config.txt`.

Naming a batch? Skip the config and type each name instead:
`.venv/bin/python teacher/name_sensor.py AIIT-YOURNAME`, with each
sensor's name in place of `AIIT-YOURNAME`.

Names: 1–20 letters, digits, `-` or `_`, no spaces. A Mac that already paired
the sensor under an old name must **Forget** it and pair again.

Don't commit `teacher/naming_config.txt` with a real name in it. Leave
`AIIT-YOURNAME` there for the next teacher.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `No such file or directory: .venv/bin/...` | Do setup steps 1–2 on this Mac, from the project folder (step 0). |
| `No name yet` | Put the new name in `teacher/naming_config.txt` and save, or type it after the command. |
| `Found 0 Mega ports` | Try another USB cable (some only charge) or port. Avoid hubs. |
| `Found 2 Mega ports` | Unplug the other Megas, or add `--port /dev/cu.usbmodem…`. |
| `HC-06 didn't answer AT` | Something is connected to the HC-06 over Bluetooth, or TX/RX are swapped. Disconnect it and run the command again. |
| `Rename failed` | Check the name: 1–20 letters, digits, `-` or `_`. |
| Upload times out (`stk500v2_getsync`) | Another USB port or cable. Close any open serial monitor. |
