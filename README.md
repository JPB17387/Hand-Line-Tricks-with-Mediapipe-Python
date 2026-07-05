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

The application supports multiple interactive, eye-catching hand effects that you can switch between on-the-fly:

- **0️⃣ Standard Glow (Classic):** Renders glowing joints and draws distance-based, color-shifting connection lines between fingertips.
- **1️⃣ Inversion Portal:** Inverts colors inside a bounding box around your hands, framed by a high-tech glowing corner HUD.
- **2️⃣ Energy Pulse:** Shoots lightning arcs between fingers (or outward radially if one hand is active) that react to movement speed.
- **3️⃣ Motion Ghost Trail:** Creates fading trails of past positions with smooth color shifting from violet to magenta.
- **4️⃣ Particle Shower:** Spawns falling glowing particles from your fingertips with simulated gravity.
- **5️⃣ Ripple Distortion:** Warps and bends the video feed like liquid ripples centered on your hands.
- **6️⃣ Thermal Vision:** Displays an infrared heat map of the scene where your hands act as hot thermal points.

*For full details on the visual effects, see [FEATURES.md](file:///c:/Users/HF/Desktop/Hand%20Tricks/FEATURES.md).*

---

## ⌨️ Live Keyboard Controls

Configure and customize settings in real-time during execution using the following key bindings:

| Command Key | Action | Details |
| :--- | :--- | :--- |
| **`0` - `6`** | Switch Effect | Select visual effect 0 through 6. |
| **`D`** | Toggle Diagnostic HUD | Toggles the overlay showing FPS, model inference latency, and blur time. |
| **`R`** | Toggle Resolution | Switches between **360p** (fast performance) and **720p** (high quality). |
| **`B`** | Cycle Glow Mode | Cycles through **Optimized Glow** (low-CPU blur), **Standard Glow**, and **Glow Off**. |
| **`Q`** | Quit / Exit | Closes all open windows and releases camera hardware resources. |

---

## 🚀 Setup & Installation

Follow these steps to get a copy of this project running on your local machine using an isolated virtual environment (`.venv`).

### 1. Clone the Repository
Copy the project to your local machine:
```bash
git clone <your-repository-url>
cd "Hand Tricks"
```

### 2. Create the Virtual Environment
Create an isolated `.venv` space:
```bash
# Windows
python -m venv .venv
```

### 3. Activate the Virtual Environment
```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.venv\Scripts\activate.bat
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

Choose your camera index from the stylized dark launcher UI, and press **Q** on your keyboard to exit at any time.

---

## ⚡ Hardware Optimizations

This project incorporates optimization techniques to run efficiently on low-spec hardware:
1. **Video Mode Landmark Tracking:** Restricts full-frame object detection passes to avoid CPU bottlenecks.
2. **Pre-allocated Frame Pools:** Cuts memory footprint and removes garbage collection stuttering.
3. **Downscaled Gaussian Blurring:** Calculates glows at a 4x lower resolution, achieving a **3.0x speedup** on blur pipelines.