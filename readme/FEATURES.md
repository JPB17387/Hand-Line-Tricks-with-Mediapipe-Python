# 🚀 Hand Tricks - Feature Documentation

This document describes all features, interactive gestures, holographic 3D objects, performance optimizations, and technical details of the **Hand Tricks** visual application.

---

## 🌀 Keyboard-Free 3D Hologram System (Iron-Man Mode)

The application features a complete **gesture-driven holographic 3D wireframe engine** (`hologram3d.py`) allowing full keyboard-free interaction. You can summon, grab, move & place anywhere on screen, rotate & tilt 360° continuously, and zoom in/out with your hands.

### ✋ Natural Hand Gestures & Controls

- **Pick Up & Place Anywhere (Drag & Drop):**
  Pinch your thumb and index finger together near the hologram to pick it up. Drag it anywhere across the webcam screen. When you release the pinch, the hologram **remains right where you dropped it** in 3D space, with natural inertial coasting. You can reach out and pick it up again at any time.

- **Continuous 360° Free Tilt & Rotation:**
  - *Translation Drag:* Moving your grabbing hand left/right spins the hologram 360° continuously around the Y-axis (yaw); moving it up/down tilts it 360° around the X-axis (pitch). Rotation is unbounded.
  - *3D Wrist Orientation:* MediaPipe calculates the 3D plane and normal vector of your hand. Tilting or twisting your wrist in 3D space directly tilts and turns the hologram to mirror your hand.
  - *Inertial Coasting:* Flicking and releasing the hologram imparts momentum, causing it to spin and glide smoothly in mid-air before damping down.

- **Zoom In and Out (Depth & Pinch Scaling):**
  - *Single-Hand Depth Zoom:* Pull your grabbing hand closer to the camera to enlarge the hologram; push it away to shrink it.
  - *Two-Hand Spread Zoom:* Bring both hands into view and move them apart to scale the hologram up, or bring them together to scale it down.
  - *Mouse Scroll:* The mouse scroll-wheel also scales the hologram when active.

- **Open-Palm Recall:**
  Holding an open flat palm directly beneath the hologram smoothly summons it back to float above your palm.

- **On-Screen Touchable HUD Widget:**
  Tap on-screen buttons with your index fingertip (or click with mouse):
  - `[3D HOLO]` : Turn hologram overlay ON / OFF.
  - `[ < ]` / `[ > ]` : Cycle between the 16 3D models.
  - `[ RECALL ]` : Center and recall hologram.
  - `[ SPIN ]` : Toggle ambient 360° auto-revolving.

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

## 🎨 Interactive Visual Effects (0–9)

Switch between real-time effects by pressing `0` through `9`:

### 0️⃣ Standard Glow (Classic Mode)
- **Description:** Draws skeletal bones and circular joint nodes within each hand independently. The bones glow with a dynamic color that transitions smoothly from green to blue and red depending on hand distance.
- **Aesthetic style:** Premium neon skeletal glow.

### 1️⃣ Inversion Portal (Negative Box)
- **Description:** Detects the boundary of your hand and creates a rectangular portal framing it. Inside the bounding box, all image colors are inverted to their negative equivalents, framed by high-contrast corner HUD brackets.
- **Best use case:** High-contrast environments.

### 2️⃣ Energy Pulse (Lightning Core)
- **Description:** Jagged lightning-bolt arcs and electric sparks discharge radially from fingertips, scaling dynamically with hand movement velocity.
- **Best use case:** Fast and expressive hand waves.

### 3️⃣ Motion Ghost Trail (Afterimage)
- **Description:** Your movements leave a fading trail of past frames behind them. Hand joints and skeletal connectors from prior positions fade out gracefully using an exponential decay opacity model.
- **Best use case:** Slow, graceful hand motions.

### 4️⃣ Particle Shower (Magical Sparkles)
- **Description:** Fingertips emit glowing neon particles that stream upward and fall back down under simulated gravity.
- **Best use case:** Dynamic gestures, drawing loops.

### 5️⃣ Ripple Distortion (Liquid/Warp)
- **Description:** The webcam frame behaves like a liquid surface. Moving your hand creates local circular ripples and lens distortions that radiate outward from your palm.
- **Best use case:** Interactive wave gestures.

### 6️⃣ Thermal Vision (Heat Mapping)
- **Description:** Transforms the frame into a hot infrared thermal visualization. Hand joints act as heat sources glowing yellow/red against a cool blue background.
- **Best use case:** High-tech radar / sci-fi aesthetics.

### 7️⃣ Particle Orbit (Gravity Well)
- **Description:** Concentric rings of glowing sparks orbit around the center of each hand like gravitational fields.
- **Best use case:** Circular motions and spell-casting poses.

### 8️⃣ Digital Rain Aura (Matrix Proximity)
- **Description:** Matrix-style streams of binary characters and alphanumeric code drift upwards from your hand joints.
- **Best use case:** Futuristic digital display demos.

### 9️⃣ Goku Power Core (Super Saiyan & Kamehameha)
- **Description:** A flaming gold Super Saiyan aura rises from all 21 hand joints. When both hands are brought close together, a massive glowing cyan Kamehameha energy ball forms between your palms with electric arcing and sound synthesis.
- **Best use case:** High-energy cosplay presentations.

---

## 📷 Photo Capture & Video Recording Systems

- **📷 Photo Button (Top-Right):** Touch or click to capture the frame. Saves as `captures/capture_YYYYMMDD_HHMMSS.png` with a camera shutter sound.
- **🔴 Record Button (Top-Right):** Touch or click to toggle AVI video recording. Saves as `captures/recording_YYYYMMDD_HHMMSS.avi` with blinking REC indicator and audio beeps.

---

## 🛠️ Live Keyboard Controls (Secondary Fallbacks)

| Key | Action | Description |
| :--- | :--- | :--- |
| **`0` - `9`** | Switch Effect | Select visual effect 0 through 9. |
| **`M`** | Toggle 3D Hologram | Summons/dismisses the 3D hologram overlay. |
| **`N`** | Next Hologram Object | Cycles through the 16 3D models (`Shift+N` goes backwards). |
| **`O`** | Toggle Hand Outline | Hides/shows the hand skeleton lines. |
| **`D`** | Toggle HUD | Shows or hides the diagnostic dashboard (FPS, latency, glow mode). |
| **`R`** | Toggle Resolution | Switches between **640x360** (Performance) and **1280x720** (Quality). |
| **`B`** | Cycle Glow Mode | Cycles through **Optimized Glow**, **Standard Glow**, and **Glow Off**. |
| **`F`** | Toggle Fullscreen | Maximizes window to borderless fullscreen. |
| **`C`** | Screenshot | Captures and saves frame to `captures/`. |
| **`V`** | Toggle Record | Starts/stops video recording. |
| **`P`** | Toggle Pinch-Zoom | Enables/disables digital camera zoom. |
| **`[` `]`** | Spin Hologram (Y) | Manually rotates active hologram left/right. |
| **`;` `'`** | Tilt Hologram (X) | Manually rotates active hologram up/down. |
| **`=` `-`** | Zoom Hologram | Manually zooms active hologram in/out. |
| **`W`** | Toggle WebSocket Server | Broadcasts landmarks on port 8765. |
| **`Q`** | Quit / Exit | Closes window and releases camera. |