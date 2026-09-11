<table align="center" width="100%">
  <tr>
    <td align="center" bgcolor="#1A1C23" style="padding: 40px; border-radius: 8px;">
      <h1><font color="#FFFFFF">OpenCV Hand Tricks & Effects</font></h1>
      <p><font color="#A0AEC0">Dynamic real-time hand tracking visualizer and holographic 3D effects engine built with Python and MediaPipe.</font></p>
    </td>
  </tr>
</table>

This is a Python-based real-time hand-tracking visualization tool that focuses on smooth, aesthetic visuals and hardware-optimized performance. It utilizes MediaPipe and OpenCV to capture hand landmarks and renders interactive visual effects driven by your movements.

It is designed to run smoothly on systems with modest resources (e.g., 4GB RAM, old Intel i5 CPUs, and low-end GPUs like the Geforce 840M) through downscaled image processing techniques and temporal tracking algorithms.

---

## Features & Visual Effects

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

---

## 🌀 100% Keyboard-Free 3D Hologram Experience (Iron-Man Mode)

You no longer need to touch any keyboard buttons to summon, manipulate, rotate, tilt, or zoom holograms! The entire 3D hologram system is operated directly with **natural hand gestures** and **on-screen touchable/clickable controls**.

Powered by [`hologram3d.py`](hologram3d.py), a real-time 3D wireframe engine featuring full 3-axis rotation ($R_x, R_y, R_z$), perspective projection, depth-based glow shading, holographic projector base disk, and ascending laser emitter beams.

### Clean Hands and Performance Modes

Landmarks are always tracked for gestures, but the camera view is clean by default: no skeletal trace is painted over the real hand. Press **`O`** only when a landmark debug view is useful. This also keeps motion trails from drawing hand bones, while pinch, drag, hold, rotate, and zoom remain active.

Press **`H`** to switch hologram rendering between **Studio** mode (translucent volume, masked scan lighting, depth highlights, and projector grid) and **Fast** mode (lower-cost depth wireframe).

### ✋ Natural Hand Gestures:

1. **Pick Up & Place Anywhere (Drag-and-Drop):**
   - Pinch your thumb and index finger together near the hologram to pick it up.
   - Move your hand anywhere on screen — the hologram follows your movement with glowing magnetic tractor beams.
   - Open your fingers to release: the hologram **stays right where you placed it**, floating in mid-air with gentle physics coasting rather than snapping back.
   - Reach out and pinch near it again anytime to pick it back up and move it somewhere else!

2. **360° Free Tilt, Spin & Rotation (All Axes):**
   - **Translation Drag:** Moving your grabbing hand left/right spins the hologram 360° around the Y-axis; moving up/down tilts it 360° around the X-axis.
   - **3D Wrist Pose:** Tilting or twisting your wrist in 3D space rotates the hologram matching your hand's orientation in real-time.
   - **Inertia Momentum:** Releasing the hologram while moving imparts momentum, letting it spin 360° freely and smoothly before settling.

3. **Zoom In and Out (Depth & Pinch Scaling):**
   - **Single-Hand Pull/Push:** Pull your grabbing hand closer to the camera to zoom in; push it away to zoom out.
   - **Two-Hand Spread Zoom:** Bring both hands into view and move them apart to enlarge the hologram, or bring them together to shrink it.
   - **Mouse Scroll:** Mouse scroll-wheel also fine-tunes zoom when needed.

4. **Recall / Snap to Palm:**
   - Hold an open flat palm directly beneath the hologram to gently summon it back above your palm.

5. **On-Screen Touchable Quick Bar:**
   - Tap buttons with your index fingertip (or mouse click):
     - `[3D HOLO]` : Turn hologram overlay ON / OFF.
     - `[ < ]` / `[ > ]` : Cycle to previous/next 3D model.
     - `[ RECALL ]` : Center and recall hologram.
     - `[ SPIN ]` : Toggle ambient idle 360° auto-revolving.

---

## 🎨 3D Hologram Model Catalog (16 Sci-Fi Models)

| Icon | Model | Description | Hologram Tint |
| :--- | :--- | :--- | :--- |
| 🚀 | **Rocket** | Multi-stage aerospace rocket with nose cone, fuselage rings, 4 swept delta stabilizer fins, nozzle bell, and glowing thrust flame plume. | Blaze Solar Amber |
| 🏠 | **House** | 3D architectural house with pitched gable roof, ridge beam, chimney, front door frame, cross-pane windows, and foundation perimeter. | Golden Amber Sand |
| 🧊 | **Tesseract** | Sci-Fi 4D Hypercube: concentric outer and inner cubes connected with hyper-struts and a central singularity core node. | Electric Cyan |
| 🌐 | **Globe** | Holographic Earth with latitude/longitude grid, equator ring, and a tilted orbital satellite ring with an orbiting satellite. | Aqua Teal |
| 🧍 | **Human** | Cybernetic humanoid android with visor helmet cage, articulated ribcage/spine, pelvis, limbs, and glowing joint hubs. | Neon Magenta |
| 🚗 | **Cyber Car** | Futuristic sports car with aerodynamic cabin, fastback roof, rear wing spoiler, front bumper/headlights, and 3D spoked wheel cylinders. | Vermilion Red |
| ✈️ | **Stealth Jet** | Supersonic stealth fighter jet with radome needle nose, cockpit bubble canopy, delta wings with wingtip missiles, canted twin fins, and afterburners. | Electric Sky Azure |
| 🏢 | **Skyscraper** | Cyber metropolis skyscraper with tiered floors, diagonal structural lattice bracing, glass elevator column, crown spire, and radio beacon antenna. | Ice Cool Cyan |
| 🔺 | **Pyramid** | Stepped Stargate hologram pyramid with multi-tier terraces, foundation perimeter, glowing apex capstone, and internal energy conduit. | Pharaoh Gold |
| ⚛️ | **Quantum Atom** | Multi-orbital atom with 4 tilted electron shells, valence electron nodes, and an octahedron nucleus core. | Electric Lime |
| 🛸 | **Star Cruiser** | Sci-fi starship with forward command saucer, bridge dome, secondary engineering hull, deflector dish, and twin warp nacelles. | Quantum Cobalt |
| 💎 | **Diamond** | Faceted brilliant-cut 3D gemstone with table facet, crown kite facets, girdle ring, and pavilion converging to a sharp culet point. | Crystal Aquamarine |
| 🧬 | **DNA Helix** | Double-helix spiral strand with intertwined backbones connected by nucleotide base-pair rungs. | Magenta-Violet |
| 🫀 | **Cyber Heart** | 3D faceted cyberpunk anatomical heart with ventricle curves, atrium chambers, and curved aortic arch conduit. | Pulsing Crimson |
| 🚁 | **Tactical Drone** | High-tech quadcopter with central fuselage pod, 4 carbon-fiber arms, 4 rotor discs, landing skids, and forward camera gimbal. | Emerald Green |
| 🛰️ | **Satellite** | Space satellite with cuboid instrument bus, dual solar panel arrays with individual grid cells, and parabolic dish antenna. | Solar Deep Cyan |

---

## Photo Capture & Video Recording

The project has interactive buttons drawn at the top-right corner of the stream window:
* Click the **Camera Icon** (or touch with index finger / press **`C`**) to take a snapshot. Saves as a PNG image in `captures/`.
* Click the **Record Dot** (or touch with index finger / press **`V`**) to toggle AVI video recording in `captures/`.
* Sound feedback (shutter beep, recording start/stop beeps) is played in the background when triggers occur.

---

## Live Keyboard Controls (Secondary Fallbacks)

While the hologram and interface can be operated 100% keyboard-free, convenient keyboard shortcuts are available:

| Command Key | Action | Details |
| :--- | :--- | :--- |
| **`0` - `9`** | Switch Effect | Select visual effect 0 through 9. |
| **`M`** | Toggle 3D Hologram | Summons/dismisses the 3D hologram overlay. |
| **`N`** | Next Hologram Object | Cycles through the 16 3D models (`Shift+N` goes backwards). |
| **`O`** | Toggle Hand Outline | Hides/shows the hand skeleton lines for a cleaner silhouette. |
| **`D`** | Toggle Diagnostic HUD | Toggles the overlay showing FPS, model inference latency, and blur time. |
| **`R`** | Toggle Resolution | Switches between **360p** (fast performance) and **720p** (high quality). |
| **`B`** | Cycle Glow Mode | Cycles through **Optimized Glow**, **Standard Glow**, and **Glow Off**. |
| **`H`** | Hologram Quality | Toggles **Studio** and **Fast** hologram rendering. |
| **`F`** | Toggle Fullscreen | Maximizes window to borderless fullscreen or standard windowed mode. |
| **`C`** | Take Screenshot | Saves the current screen frame to the `captures/` directory. |
| **`V`** | Toggle Video Record | Toggles AVI video recording to the `captures/` directory. |
| **`P`** | Toggle Pinch-Zoom | Enables/disables the digital camera zoom. |
| **`[` `]`** | Spin Hologram (Y-axis) | Manually rotates the active hologram left/right. |
| **`;` `'`** | Tilt Hologram (X-axis) | Manually rotates the active hologram up/down. |
| **`=` `-`** | Zoom Hologram | Manually zooms the active hologram in/out. |
| **`W`** | Toggle WebSocket Server | Broadcasts hand landmarks as JSON on port 8765 for remote 3D clients. |
| **`Q`** | Quit / Exit | Closes all open windows and releases camera hardware resources. |

---

## Quick Start (Get Running in 2 Minutes)

**Windows:** Double-click `RUN.bat`

**macOS/Linux:** Run `bash RUN.sh`

**Or see [QUICK_START.md](readme/QUICK_START.md) for detailed options.**

---

## Setup & Installation

Follow these steps to get a copy of this project running on your local machine using an isolated virtual environment (`.venv`).

> **Python Version Requirement:** MediaPipe supports **Python 3.8 – 3.12**.

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd "Hand Tricks"
```

### 2. Create the Virtual Environment
```bash
python -m venv .venv
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
```bash
python main.py
```