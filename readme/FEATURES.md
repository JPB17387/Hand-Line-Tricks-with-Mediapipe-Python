## New Features (Added)

- Toggle hand outline visibility with the `O` key.
- Summon a **holographic 3D object** anchored to the palm with the `M` key; pinch to grab it, rotate it 360° on both axes, and zoom it in/out (see below).
- Cycle through the 3D object library with the `N` key (`Shift+N` to go backwards).
- Pinch-to-zoom (digital zoom) is enabled by default; toggle with the `P` key.
- Start a lightweight WebSocket landmark broadcaster (ws://0.0.0.0:8765) with the `W` key.

These additions extend the interactivity while keeping existing visual effects unchanged.

### 🌀 Holographic 3D Objects (Iron-Man Mode)

Press `M` to bring up a glowing wireframe hologram floating above your palm, powered by the standalone [`hologram3d.py`](../hologram3d.py) engine — real 3D rotation matrices and perspective projection (not a flat sprite), with depth-based glow shading and a holographic "projector disc" base under the object.

**Object library (cycle with `N` / `Shift+N`):**

| Object | Description |
| :--- | :--- |
| 🧊 **Cube** | The original wireframe box, now with true 3D depth shading. |
| 🌐 **Globe** | A latitude/longitude wireframe sphere — spin it like a holographic Earth. |
| 🧍 **Human** | A humanoid stick-figure skeleton (head to feet). |
| 🚗 **Car** | A wireframe car body, cabin, and four wheels. |
| ✈️ **Plane** | A fuselage, wing pair, and tail fin built from tapered rings. |
| 🏢 **Building** | A multi-floor tower with a rooftop antenna. |
| 🔺 **Pyramid** | A simple four-sided pyramid. |
| ⚛️ **Atom** | Three tilted electron-orbit rings around a nucleus. |

New objects can be added by writing a small model-builder function in `hologram3d.py` (see [CODE_STRUCTURE.md](CODE_STRUCTURE.md)) — no changes to `main.py` are needed beyond that.

**Grab, rotate, and zoom:**
- **Grab & move:** pinch your thumb and index finger together near the hologram to grab it; it follows your fingertip while grabbed.
- **Rotate 360° on X and Y:** while grabbed, moving your hand left/right spins the object around the Y-axis, and moving it up/down tilts it around the X-axis. Rotation is unbounded — you can keep spinning continuously past 360° on either axis, at the same time.
- **Zoom in/out two ways:** pull your grabbing hand closer to the camera to zoom in (and push it away to zoom out), based on how large your hand appears on screen — or show both hands and spread them apart / bring them together, like a phone's pinch-to-zoom. Both work simultaneously.
- **Keyboard fallback:** `[` / `]` spin Y, `;` / `'` tilt X, `=` / `-` zoom, and the mouse scroll-wheel also zooms while the hologram is active.

Enhancements:

- Inertia: when you release a grabbed hologram it keeps spinning/coasting and decays naturally using damping.
- Snap-to-palm: if the hologram gets close to your palm it gently snaps back and stabilizes.
- Depth-shaded wireframe: edges nearer the camera render brighter and thicker, edges farther away dim — this is what makes the 360° rotation read clearly as real 3D rather than a flat shape.
- Each object has its own holographic tint color (cyan-gold globe, violet human, orange-red car, etc).
- When the hologram or pinch-zoom is active, the palm skeletal lines are suppressed to give a cleaner silhouette.


# 🚀 Hand Tricks - Feature Documentation

This document describes all features, interactive keyboard controls, performance optimizations, and technical details of the **Hand Tricks** visual application.

---

## 🎨 Interactive Visual Effects

You can toggle between different eye-catching effects in real-time by pressing the corresponding number keys (`0` to `9`) on your keyboard.

### 0️⃣ Standard Glow (Classic Mode)
* **Description:** Draws skeletal bones and circular joint nodes within each hand independently. The bones glow with a dynamic color that transitions smoothly from green, to blue, and then red, depending on the relative physical distance between your hands. No lines cross between the two hands.
* **Aesthetic style:** Premium neon skeletal glow.

### 1️⃣ Inversion Portal (Negative Box)
* **Description:** Detects the boundary of your hand and creates a rectangular portal framing it. Inside the bounding box, all image colors are inverted to their negative equivalents. The border of the box pulses dynamically with a high-contrast neon corner HUD styling. (Optimized with a minimum thickness safety floor to prevent rendering errors).
* **Best use case:** High-contrast environments.

### 2️⃣ Energy Pulse (Lightning Core)
* **Description:** Jagged lightning-bolt arcs and electric sparks discharge radially from the fingertips of both hands. The jaggedness, intensity, and length of the discharges dynamically scale with the speed of your hand movements. All discharges are self-contained on each hand, meaning no lines connect the two hands.
* **Best use case:** Fast and expressive hand waves.

### 3️⃣ Motion Ghost Trail (Afterimage)
* **Description:** Your movements leave a fading trail of past frames behind them. Hand joints and skeletal bone connectors from prior positions fade out gracefully using an exponential decay opacity model. The trail shifts color (violet to pink) as it ages.
* **Best use case:** Slow, graceful hand motions.

### 4️⃣ Particle Shower (Magical Sparkles)
* **Description:** Fingertips emit glowing neon particles that stream upward and fall back down under simulated gravity. The number of spawned particles scales with hand velocity. The particles gradually shrink and fade away over time.
* **Best use case:** Dynamic gestures, drawing loops.

### 5️⃣ Ripple Distortion (Liquid/Warp)
* **Description:** The webcam frame behaves like a liquid surface. Moving your hand creates local circular ripples and lens distortions that radiate outward from your hand's center (MCP joint). The wave amplitude increases when you move your hand quickly.
* **Best use case:** Interactive wave gestures.

### 6️⃣ Thermal Vision (Heat Mapping)
* **Description:** Transforms the frame into a hot infrared thermal visualization using a colormap. The hand joints act as heat sources, making the hands glow white/yellow/red, while the background shifts to cold, darkened blue.
* **Best use case:** Creating a sci-fi/high-tech radar aesthetic.

### 7️⃣ Particle Orbit (Gravity Well)
* **Description:** Creates concentric rings of glowing sparks that orbit around the center of each hand (MCP joint). The orbit speed and radius dynamically swell and contract based on the hand's speed. The hand center itself pulses with a glowing core.
* **Best use case:** Slow circular motions or magical spell-casting poses.

### 8️⃣ Digital Rain Aura (Matrix Proximity)
* **Description:** Matrix-style streams of binary characters and alphanumeric code drift upwards from your hand joints. The characters scale down and dissolve as they ascend, wrapping your hands in a green digital aura.
* **Best use case:** Futuristic digital display demos.

### 9️⃣ Goku Power Core (Super Saiyan & Kamehameha) - *NEW*
* **Description:** A flaming gold Super Saiyan aura rises from all 21 hand joints. If both hands are brought close together (distance < 240px), a massive glowing cyan Kamehameha energy ball forms between your palms. The core crackles with energy, and high-voltage lightning charges into it from both hands, accompanied by a synthesizer charging sound sweep.
* **Best use case:** High-energy martial arts / cosplay presentations.

---

## 📷 Photo Capture & Video Recording Systems

The application includes on-screen touch/click buttons in the top-right corner, backed by keyboard hotkeys:

### On-Screen Interface
* **📷 Photo Button (Left):** Click to capture the current frame. Saves as `captures/capture_YYYYMMDD_HHMMSS.png` with a shutter sound beep.
* **🔴 Record Button (Right):** Click to toggle video recording. Saves as `captures/recording_YYYYMMDD_HHMMSS.avi` (using standard XVID encoding). The red dot blinks, and a "● RECING" indicator flashes on the screen while active, accompanied by double-beep start/stop indicators.

---

## 🔊 Sound Effects Engine

To provide immersive auditory feedback without stalling frame execution, the system uses **asynchronous background threads** utilizing Windows' built-in `winsound` synthesizer:
* **Screenshot Shutter:** A high-pitched camera shutter beep.
* **Recording Toggles:** Two-tone double beeps signaling start and stop.
* **Kamehameha Charge:** A sliding frequency synthesizer sweep that builds pitch as the energy ball builds size.

---

## 🖥️ Full Desktop Layout & Fullscreen

* **Windows Scaling:** The application uses `cv2.WINDOW_NORMAL`, allowing you to drag to maximize, shrink, or resize the window to any resolution. Hardware scaling handles projection, maintaining the high performance of 360p or 720p internal tracking while filling your screen.
* **Fullscreen Hotkey:** Press the **`F`** key to switch between borderless fullscreen mode and standard windowed mode instantly.

---

## 🦴 Isolated Hand Skeletal Connections

A key aesthetic change has been applied: **the application no longer draws lines connecting your two hands together in any effect.** 
Instead, each hand's structure is visualized internally using the standard 21 hand landmarks connected by a neon skeleton overlay:
* Connects wrist to fingertips along all 5 digits.
* Draws concentric circles around joints to emphasize articulation.
* Helps distinguish hand movement features independently.

---

## 🛠️ Performance & Configuration Controls

To keep the application running smoothly on lightweight setups, the following live configuration keys are available:

| Key | Action | Description |
| :--- | :--- | :--- |
| **`0` - `9`** | Switch Effect | Select visual effect 0 through 9. |
| **`D`** | Toggle HUD | Shows or hides the diagnostic dashboard displaying real-time FPS, inference latency, rendering cost, and active resolution. |
| **`R`** | Toggle Resolution | Switches capture resolution between **640x360** (Performance Mode) and **1280x720** (Quality Mode) on the fly, safely restarting camera streams. |
| **`B`** | Cycle Glow Mode | Cycles through **Optimized Glow** (blurs at 4x downsample, saving 70% CPU cycles), **Standard Glow** (direct heavy blur), and **Glow Off**. |
| **`F`** | Toggle Fullscreen | Maximizes the window to full screen. |
| **`C`** | Screenshot | Captures and saves the frame. |
| **`V`** | Toggle Record | Starts/stops video recording. |
| **`O`** | Toggle Hand Outline | Hides/shows the hand skeleton lines. |
| **`M`** | Toggle 3D Hologram | Summons/hides the holographic 3D object (grab, rotate, zoom). |
| **`N`** | Next Hologram Object | Cycles Cube → Globe → Human → Car → Plane → Building → Pyramid → Atom (`Shift+N` reverses). |
| **`P`** | Toggle Pinch-Zoom | Enables/disables the digital camera zoom. |
| **`[` `]`** | Spin Hologram (Y) | Manually rotates the active hologram left/right. |
| **`;` `'`** | Tilt Hologram (X) | Manually rotates the active hologram up/down. |
| **`=` `-`** | Zoom Hologram | Manually zooms the active hologram in/out. |
| **`W`** | Toggle WebSocket Server | Broadcasts hand landmarks as JSON on port 8765. |
| **`Q`** | Quit | Releases camera, stops recordings, and exits. |

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