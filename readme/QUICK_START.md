### New Controls (Added)

- `O` : Toggle hand outline/lines off/on.
- `M` : Toggle faux 3D cube overlay (pinch to grab and move).
- `P` : Toggle pinch-to-zoom behavior.
- `W` : Start lightweight WebSocket streamer on port 8765 for remote clients.

Additional cube controls:

- `[` / `]` : Rotate cube left/right (Y axis)
- `;` / `'` : Tilt cube up/down (X axis)
- `=` / `-` : Increase / decrease cube size

When cube/zoom is active, palm skeletal lines are hidden for visual clarity.

# Quick Start Guide

Get **Hand Tricks** running in less than 5 minutes!

---

## ✅ Prerequisites

- **Python 3.12** (MediaPipe requirement: Python 3.8–3.12 only)
- **Windows, macOS, or Linux**
- A working webcam
- ~200 MB free disk space

---

## Option 1: Run with Script (Easiest)

### Windows

Double-click `RUN.bat` in the project folder.

The application will launch automatically with the camera selector dialog.

### macOS/Linux

```bash
chmod +x RUN.sh
./RUN.sh
```

Or in terminal:
```bash
bash RUN.sh
```

---

## Option 2: Command Line (Manual)

### Windows (PowerShell)

```powershell
cd "C:\Path\To\Hand Tricks"
.\.venv\Scripts\Activate.ps1
python main.py
```

### Windows (Command Prompt)

```cmd
cd "C:\Path\To\Hand Tricks"
.venv\Scripts\activate.bat
python main.py
```

### macOS/Linux

```bash
cd /path/to/Hand\ Tricks
source .venv/bin/activate
python main.py
```

---

## Option 3: Run in IDE (VS Code / PyCharm)

### VS Code
1. Open the `Hand Tricks` folder
2. Press `Ctrl+Shift+P` → "Python: Select Interpreter"
3. Choose `.venv` interpreter
4. Click the ▶ Play button on `main.py`

### PyCharm
1. Open the `Hand Tricks` folder
2. Go to `File → Settings → Project → Python Interpreter`
3. Set it to `.venv\Scripts\python.exe`
4. Right-click `main.py` → Run

---

## First Launch

When you run the app:

1. **Camera Selector Dialog** appears
   - Click your camera (usually "Camera 0 (Built-in Camera)")
2. **Live video** starts with a hand effect
3. **Press keys** to interact:
   - **0-9** → Switch effects
   - **R** → Toggle resolution (360p/720p)
   - **B** → Toggle glow mode
   - **F** → Toggle fullscreen
   - **C** → Capture photo
   - **V** → Record video
   - **D** → Toggle diagnostic HUD
   - **Q** → Quit

---

## Setup Verification

If you see **"Missing required Python packages..."**, run this:

```bash
pip install -r requirements.txt
```

Then verify:

```bash
python -c "import cv2, mediapipe, numpy; print('All dependencies OK!')"
```

---

## Troubleshooting

| Problem | Solution |
| :--- | :--- |
| **"No cameras found"** | Plug in webcam, close other camera apps (Zoom, Teams) |
| **"ModuleNotFoundError: cv2"** | Run `pip install -r requirements.txt` |
| **Very low FPS** | Press **R** for 360p, press **B** for optimized glow |
| **Camera selector won't appear** | Run from terminal, not through IDE |
| **No video window** | Ensure no other app is using the camera |

For more help, see **[TROUBLESHOOTING.md](readme/TROUBLESHOOTING.md)**.

---

## What to Read Next

- **[README.md](README.md)** – Full project overview
- **[FEATURES.md](readme/FEATURES.md)** – All 10 visual effects explained
- **[IDE_SETUP_GUIDE.md](readme/IDE_SETUP_GUIDE.md)** – Detailed IDE setup
- **[TROUBLESHOOTING.md](readme/TROUBLESHOOTING.md)** – Common issues & fixes

---

## Ready to Go!

Your Hand Tricks application is ready to run. Choose an option above and launch!

**Enjoy the effects!** 🚀

---


## Buy me a coffee
Donate some money to support my work.  <br>Thank you! :)
<br>
<br>

>Click the button below to donate:

<a href="https://buymeacoffee.com/paulb_codebreaker" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174">
</a>
<br>
<br>
<br>

>Or scan this QR Code to donate:

<p align="center" >
  <img src="./public/Photos/buy-me-a-coffe-qr-code.png" alt="Centered Logo" width="400" height="400">
</p>