<table align="center" width="100%">
  <tr>
    <td align="center" bgcolor="#1A1C23" style="padding: 40px; border-radius: 8px;">
      <h1><font color="#FFFFFF">OpenCV Hand Tricks & Effects</font></h1>
      <p><font color="#A0AEC0">Dynamic real-time hand tracking visualizer and effects engine built with Python and MediaPipe.</font></p>
    </td>
  </tr>
</table>

This is a Python-based real-time hand-tracking visualization tool that focuses on smooth, aesthetic visuals and hardware-optimized performance. It utilizes MediaPipe and OpenCV to capture hand landmarks and renders interactive visual effects driven by your movements.

It is designed to run smoothly on systems with modest resources (e.g., 4GB RAM, old Intel i5 CPUs, and low-end GPUs like the Geforce 840M) through downscaled image processing techniques and temporal tracking algorithms.

---

## ✨ Features & Visual Effects

The application supports multiple interactive, eye-catching hand effects that you can switch between on-the-fly. **Note that in all effects, hands are visualized independently, with no lines or arcs connecting your two hands together.**

- **0️⃣ Standard Glow (Classic):** Renders glowing skeletal joints within each hand and draws distance-based color-shifting lines.
- **1️⃣ Inversion Portal:** Inverts colors inside a bounding box around each hand, framed by a high-tech glowing corner HUD.
- **2️⃣ Energy Pulse:** Shoots lightning arcs and sparks radiating out of your fingertips that react to movement speed.
- **3️⃣ Motion Ghost Trail:** Creates fading trails of past positions with smooth color shifting from violet to magenta.
- **4️⃣ Particle Shower:** Spawns falling glowing particles from your fingertips with simulated gravity.
- **5️⃣ Ripple Distortion:** Warps and bends the video feed like liquid ripples centered on your hands.
- **6️⃣ Thermal Vision:** Displays an infrared heat map of the scene where your hands act as hot thermal points.
- **7️⃣ Particle Orbit:** Concentric rings of glowing sparks that orbit around each hand center like gravitational fields.
- **8️⃣ Digital Rain Aura:** Streams green binary and matrix code floating upwards from your hand joints.
- **9️⃣ Goku Power Core:** A flaming gold Super Saiyan aura rises from hand joints, forming a pulsing cyan Kamehameha energy ball when hands get close, backed by a synth charging sound.

*For full details on the visual effects, see [FEATURES.md](readme/FEATURES.md).*

## 🆕 New Interactive Features

- `O` : Toggle hand outline/lines off/on (useful for a cleaner silhouette).
- `M` : Toggle a faux 3D cube overlay anchored to your palm; use a pinch gesture to grab and move the cube.
- `P` : Toggle pinch-to-zoom (digital zoom centered on hand/palm).
- `W` : Start a simple WebSocket streamer on port 8765 to broadcast landmarks as JSON for remote 3D clients or devices.

These features are additive and do not remove or change the original visual effects — they provide additional interactivity and integration points.

---

## 📷 Photo Capture & Video Recording

The project has interactive buttons drawn at the top-right corner of the stream window:
* Click the **Camera Icon** or press the **`C`** key to take a snapshot. Saves as a PNG image.
* Click the **Record Dot** or press the **`V`** key to toggle video recording. Saves as an XVID AVI video.
* All saved media is automatically created and stored inside the `captures/` folder in the project root.
* Sound feedback (shutter beep, recording start/stop beeps) is played in the background when triggers occur.

---

## ⌨️ Live Keyboard Controls

Configure and customize settings in real-time during execution using the following key bindings:

| Command Key | Action | Details |
| :--- | :--- | :--- |
| **`0` - `9`** | Switch Effect | Select visual effect 0 through 9. |
| **`D`** | Toggle Diagnostic HUD | Toggles the overlay showing FPS, model inference latency, and blur time. |
| **`R`** | Toggle Resolution | Switches between **360p** (fast performance) and **720p** (high quality) while safely restarting camera feeds. |
| **`B`** | Cycle Glow Mode | Cycles through **Optimized Glow** (low-CPU blur), **Standard Glow**, and **Glow Off**. |
| **`F`** | Toggle Fullscreen | Maximizes the window to borderless fullscreen or scales back to windowed mode. |
| **`C`** | Take Screenshot | Saves the current screen frame to the `captures/` directory. |
| **`V`** | Toggle Video Record | Toggles AVI video recording to the `captures/` directory. |
| **`Q`** | Quit / Exit | Closes all open windows and releases camera hardware resources. |

---

## ⚡ Quick Start (Get Running in 2 Minutes)

**Windows:** Double-click `RUN.bat`

**macOS/Linux:** Run `bash RUN.sh`

**Or see [QUICK_START.md](QUICK_START.md) for detailed options.**

---

## 🚀 Setup & Installation

Follow these steps to get a copy of this project running on your local machine using an isolated virtual environment (`.venv`).

> ⚠️ **Python Version Requirement:** MediaPipe only supports **Python 3.8 – 3.12**. Python 3.13 and 3.14 will **not** work. If you don't have Python 3.12, install it via `winget install Python.Python.3.12` or download from [python.org](https://www.python.org/downloads/release/python-3129/).

### 1. Clone the Repository
Copy the project to your local machine:
```bash
git clone <your-repository-url>
cd "Hand Tricks"
```

### 2. Create the Virtual Environment
Create an isolated `.venv` space using **Python 3.12**:
```bash
# Windows (if Python 3.12 is your default)
python -m venv .venv

# Windows (if you have multiple Python versions, use full path)
"C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" -m venv .venv
```

### 3. Activate the Virtual Environment
```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Launch the Application
Ensure the virtual environment is activated and execute:
```bash
python main.py
```

Choose your camera index from the launcher UI, and press **Q** on your keyboard to exit at any time.

### 📖 IDE-Specific Instructions
For detailed instructions on running this project in **VS Code**, **PyCharm**, **Sublime Text**, **IDLE**, or **terminal**, see the [IDE Setup Guide](readme/IDE_SETUP_GUIDE.md).

---

## 🐛 Recent Bug Fixes

**Fixed in Latest Update:**
- ✅ **Recording Indicator Typo** (Line 853, main.py)
  - **Issue:** On-screen text displayed `"● RECING"` instead of `"● RECORDING"` during video capture
  - **Fix:** Corrected text to `"● RECORDING"`
  - **Impact:** Improved UI clarity during video recording

For full changelog and version history, see [CHANGELOG.md](readme/CHANGELOG.md).

---

## ⚡ Hardware Optimizations

This project incorporates optimization techniques to run efficiently on low-spec hardware:
1. **Video Mode Landmark Tracking:** Restricts full-frame object detection passes to avoid CPU bottlenecks.
2. **Pre-allocated Frame Pools:** Cuts memory footprint and removes garbage collection stutters.
3. **Downscaled Gaussian Blurring:** Calculates glows at a 4x lower resolution, achieving a **3.0x speedup** on blur pipelines.
4. **Desktop Hardware Scaling:** Automatically scales the processed image to fill any fullscreen layout window, leveraging GPU window rendering instead of high-CPU capture resizing.

---

## 📚 Documentation

The project includes comprehensive documentation for various aspects:

| Document | Purpose |
| :--- | :--- |
| **[CHANGELOG.md](readme/CHANGELOG.md)** | Version history, bug fixes, and feature releases |
| **[CODE_STRUCTURE.md](readme/CODE_STRUCTURE.md)** | Deep dive into code architecture, class/function reference, and performance optimizations |
| **[DEVELOPMENT.md](readme/DEVELOPMENT.md)** | Guide for developers: adding effects, code style, debugging, testing, and profiling |
| **[TROUBLESHOOTING.md](readme/TROUBLESHOOTING.md)** | Common issues, solutions, and optimization tips |
| **[FEATURES.md](readme/FEATURES.md)** | Detailed descriptions of all 10 visual effects |
| **[IDE_SETUP_GUIDE.md](readme/IDE_SETUP_GUIDE.md)** | IDE-specific setup instructions (VS Code, PyCharm, Sublime, IDLE, Terminal) |

---

## 🎯 Quick Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **"ModuleNotFoundError: No module named 'mediapipe'"** | Activate virtual environment: `.\.venv\Scripts\Activate.ps1` (Windows) or `source .venv/bin/activate` (Unix) |
| **Python 3.13+ installation fails** | MediaPipe only supports Python 3.8–3.12. Install Python 3.12 first. |
| **Very low FPS (< 10 Hz)** | Press **R** for 360p, press **B** for Optimized Glow, press **D** to hide HUD |
| **Hand detection not working** | Improve lighting, check hand_landmarker.task exists, adjust confidence thresholds in main.py |
| **Videos won't play** | Ensure XVID codec installed (K-Lite Codec Pack on Windows) |
| **No audio on Windows** | Check volume levels, unmute speaker, verify audio device enabled |

For more detailed troubleshooting, see [TROUBLESHOOTING.md](readme/TROUBLESHOOTING.md).

---