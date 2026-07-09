# Running Hand Tricks in Different IDEs

This guide explains how to set up and run the **Hand Tricks** project in various editors and IDEs on Windows. The instructions also include notes for macOS and Linux users.

> **⚠️ Critical Requirement: Python Version**
>
> MediaPipe currently only supports **Python 3.8 – 3.12**. Python 3.13 and 3.14 are **NOT supported** and will fail during `pip install mediapipe`.
>
> If you only have Python 3.13+, install Python 3.12 first:
> ```
> winget install Python.Python.3.12
> ```
> Or download it from [python.org/downloads](https://www.python.org/downloads/release/python-3129/).

> **📝 Note: `winsound` Module**
>
> The project uses the `winsound` module for audio feedback (shutter beeps, recording sounds). This module is **Windows-only** and is included with Python on Windows by default. On macOS/Linux, the sound effects will simply be skipped silently (they are wrapped in try/except blocks).

---

## Prerequisites (All IDEs)

Before opening the project in any IDE, you need a working virtual environment. Run these commands **once** in a terminal:

### Step 1: Open a Terminal in the Project Folder

Navigate to the project root directory (the folder containing `main.py`).

### Step 2: Create the Virtual Environment

Use Python 3.12 specifically (not 3.13 or 3.14):

**Windows (PowerShell):**
```powershell
# If Python 3.12 is your default:
python -m venv .venv

# If you have multiple Python versions, use the full path:
& "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python312\python.exe" -m venv .venv
```

**Windows (Command Prompt):**
```cmd
"C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" -m venv .venv
```

**macOS / Linux:**
```bash
python3.12 -m venv .venv
```

### Step 3: Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** This installs `opencv-python`, `mediapipe`, and `numpy`.
> If you see `ModuleNotFoundError: No module named 'cv2'`, make sure the venv is active and run the command again.

### Step 5: Verify Installation

```bash
python -c "import cv2; import mediapipe; print('All good! OpenCV:', cv2.__version__, '| MediaPipe:', mediapipe.__version__)"
```

You should see version numbers printed with no errors.

---

## Visual Studio Code (VS Code)

### Setup

1. **Install the Python Extension**: Open VS Code → Extensions panel (`Ctrl+Shift+X`) → search for **"Python"** by Microsoft → Install.

2. **Open the Project Folder**: `File → Open Folder...` → select the `Hand Tricks` folder.

3. **Select the Python Interpreter**:
   - Press `Ctrl+Shift+P` → type **"Python: Select Interpreter"**
   - Choose the interpreter from `.venv` — it will look like:
     ```
     Python 3.12.x ('.venv': venv)  .\.venv\Scripts\python.exe
     ```
   - If it doesn't appear, click **"Enter interpreter path..."** and browse to:
     ```
     .venv\Scripts\python.exe
     ```

4. **Verify Terminal Uses the venv**: Open a new terminal (`Ctrl+`` `) and confirm you see `(.venv)` in the prompt.

### Running the App

**Option A — Terminal:**
```bash
python main.py
```

**Option B — Run Button:**
Open `main.py` and click the ▶ Play button in the top-right corner.

**Option C — Debug (F5):**
Press `F5` to launch with the debugger using the included `launch.json` configuration. This lets you set breakpoints and inspect variables.

### Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'cv2'` | The virtual environment is not activated or dependencies are not installed. Activate `.venv` and run `pip install -r requirements.txt`. |
| `ModuleNotFoundError: No module named 'mediapipe'` | Wrong interpreter selected. Press `Ctrl+Shift+P` → "Python: Select Interpreter" → pick the `.venv` one. |
| `The term 'python' is not recognized` | Open a new terminal after selecting the interpreter. The old terminal may not have the venv activated. |
| PowerShell says "running scripts is disabled" | Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Camera window doesn't appear | Make sure no other app is using your webcam. Try a different camera index in the launcher. |

---

## PyCharm (JetBrains)

### Setup

1. **Open the Project**: `File → Open` → select the `Hand Tricks` folder.

2. **Configure the Python Interpreter**:
   - Go to `File → Settings → Project: Hand Tricks → Python Interpreter`
   - Click the ⚙ gear icon → **"Add Interpreter" → "Existing"**
   - Browse to: `.venv\Scripts\python.exe` (Windows) or `.venv/bin/python` (macOS/Linux)
   - Click **OK**

3. **Verify Packages**: In the Python Interpreter settings panel, you should see `opencv-python`, `mediapipe`, and `numpy` listed.

### Running the App

**Option A — Right-click:**
Right-click `main.py` in the Project panel → **"Run 'main'"**

**Option B — Green Play Button:**
Open `main.py` → Click the green ▶ button next to `if __name__ == '__main__':` on the last line.

**Option C — Terminal:**
Open PyCharm's terminal (`Alt+F12`) and run:
```bash
python main.py
```

### Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError` | Check the interpreter is set to the `.venv` version. Go to `File → Settings → Project → Python Interpreter`. |
| PyCharm shows "No Python interpreter configured" | Click "Configure Python Interpreter" in the yellow banner and point it to `.venv\Scripts\python.exe`. |
| Slow indexing of `mediapipe` | This is normal on first open. Wait for the progress bar at the bottom to finish. |

---

## Sublime Text

### Setup

1. **Open the Folder**: `File → Open Folder...` → select the `Hand Tricks` folder.

2. **Build System** (Optional): Create a build system for running with the venv:
   - `Tools → Build System → New Build System...`
   - Paste the following and save as `HandTricks.sublime-build`:

   **Windows:**
   ```json
   {
       "cmd": ["${folder}/.venv/Scripts/python.exe", "$file"],
       "selector": "source.python",
       "working_dir": "${folder}"
   }
   ```

   **macOS / Linux:**
   ```json
   {
       "cmd": ["${folder}/.venv/bin/python", "$file"],
       "selector": "source.python",
       "working_dir": "${folder}"
   }
   ```

### Running the App

**Option A — Build System:**
Open `main.py` → Select `Tools → Build System → HandTricks` → Press `Ctrl+B`.

**Option B — Terminal:**
Open a terminal in the project folder, activate the venv, and run:
```bash
python main.py
```

---

## IDLE (Python's Built-in IDE)

### Setup

1. **Launch IDLE from the venv** (important — don't use the system IDLE):

   **Windows (PowerShell):**
   ```powershell
   .\.venv\Scripts\python.exe -m idlelib.idle
   ```

   **macOS / Linux:**
   ```bash
   .venv/bin/python -m idlelib.idle
   ```

2. This opens IDLE with the virtual environment's packages available.

### Running the App

1. In IDLE: `File → Open...` → navigate to `main.py`
2. Press `F5` (or `Run → Run Module`)

> **Note:** IDLE has limited terminal/console support. The tkinter camera selector should work, but keyboard controls in the OpenCV window will also work since they're handled by OpenCV's own event loop, not the terminal.

---

## Terminal / Command Line (No IDE)

If you prefer running without any IDE:

**Windows (PowerShell):**
```powershell
cd "C:\path\to\Hand Tricks"
.\.venv\Scripts\Activate.ps1
python main.py
```

**Windows (Command Prompt):**
```cmd
cd "C:\path\to\Hand Tricks"
.venv\Scripts\activate.bat
python main.py
```

**macOS / Linux:**
```bash
cd /path/to/Hand\ Tricks
source .venv/bin/activate
python main.py
```

---

## General Troubleshooting

### "pip install mediapipe" Fails

| Error | Cause | Fix |
|---|---|---|
| `ERROR: No matching distribution found for mediapipe` | Python version too new (3.13+) | Install Python 3.12 and recreate the venv |
| `error: Microsoft Visual C++ 14.0 or greater is required` | Missing C++ build tools | Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) |
| `pip: command not found` / `No module named pip` | Broken Python install (e.g., MSYS2) | Use a standard CPython install from [python.org](https://www.python.org) |

### Camera Issues

- **"No cameras found"**: Make sure your webcam is plugged in and not being used by another application (Zoom, Teams, etc.).
- **Black screen or crash**: Try switching to a different camera index in the launcher dialog.
- **Low FPS**: Press `R` to toggle down to 360p resolution for better performance.

### Virtual Environment Tips

- Always activate the virtual environment before running `python main.py`.
- If you see `ModuleNotFoundError`, you're likely using the wrong Python (system Python instead of the venv's).
- To verify: run `python -c "import sys; print(sys.executable)"` — it should print a path containing `.venv`.

---

## Quick Reference

| IDE | Interpreter Config Location | How to Run |
|---|---|---|
| **VS Code** | `Ctrl+Shift+P` → "Python: Select Interpreter" | ▶ Play button, `F5`, or terminal |
| **PyCharm** | `File → Settings → Project → Python Interpreter` | Right-click → Run, green ▶, or terminal |
| **Sublime Text** | Custom Build System file | `Ctrl+B` or terminal |
| **IDLE** | Launch IDLE from `.venv` Python | `F5` in editor |
| **Terminal** | Activate venv first | `python main.py` |
