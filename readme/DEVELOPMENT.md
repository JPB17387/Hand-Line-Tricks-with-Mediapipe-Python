## Development & Architecture Guide

### Current Rendering Notes

`AppState.hide_hand_lines` controls only visual overlays, not MediaPipe tracking: clean mode suppresses both the debug skeleton and motion ghost bones while pinch, drag, rotation, and zoom continue to use the landmarks. `AppState.holo_quality` selects `0` Fast or `1` Studio rendering. Fast mode skips masked volume lighting and the projector grid to reduce CPU work at larger resolutions.

When developing, customizing, or extending the **Hand Tricks** project, review the following architecture notes:

### 1. Codebase Structure & Modules

- **`main.py`**:
  - Core entry point, camera capture loop, and MediaPipe inference pipeline.
  - State machine (`AppState`) managing visual effects, physics velocity vectors, gesture detection, touch UI button dwell timers, and recording.
  - Interactive gesture engine: pick-up/drop placement, 360° drag rotation, 3D hand orientation tracking, depth zooming, and open-palm recall.
  - Audio synthesizer background threads (`winsound`).

- **`hologram3d.py`**:
  - Standalone, high-performance 3D holographic engine requiring only NumPy and OpenCV.
  - 16 procedural 3D model builders (Rocket, House, Tesseract, Globe, Human, Car, Plane, Building, Pyramid, Atom, Spaceship, Diamond, DNA, Heart, Drone, Satellite).
  - Full 3-axis rotation matrix math (`rotate_xyz(v, rx, ry, rz)`) for pitch, yaw, and roll.
  - Perspective camera projection (`project(v, center, pixel_size, focal)`).
  - Depth-shaded wireframe renderer with holographic projector disc base, ascending emitter laser lines, and glowing vertex hubs.

- **`ws_server.py`**:
  - Lightweight async WebSocket server broadcasting raw 3D landmark data as JSON on `ws://0.0.0.0:8765`.

---

### 2. Hologram Interaction Implementation Details

- **Pick-and-Place Physics:**
  - When the user pinches near the hologram, `state.grabbed` becomes `True` and `state.cube['is_placed']` is set to `True`.
  - While grabbed, the hologram follows hand coordinates directly.
  - On release, the hologram preserves its position $(x, y)$ with decaying inertial velocities (`cube['damping']`), staying exactly where the user placed it rather than snapping back.
  - Re-grabbing can occur anywhere on the canvas by reaching toward the hologram and pinching.

- **360° Tilt & Rotation Math:**
  - *Drag Delta:* Fingertip movement translates directly into angular velocity ($R_y$ yaw and $R_x$ pitch). Angles are stored **unbounded** in `state.cube['rot_x']` and `state.cube['rot_y']`, allowing infinite 360° continuous spinning.
  - *3D Wrist Pose:* `estimate_hand_orientation()` computes 3D Euler angles from the landmark plane (wrist, index MCP, middle MCP, pinky MCP). Tilting or twisting the hand applies delta rotations to $R_x, R_y, R_z$.
  - *Auto-spin:* When idle, `state.cube['auto_spin']` applies a gentle $+0.55^\circ/\text{frame}$ ambient revolution.

- **Zoom Scaling Modes:**
  - *Single-Hand Depth Zoom:* Compares the on-screen span of the grabbing hand (wrist to middle-fingertip) against `state.holo_grab_span`.
  - *Two-Hand Spread Zoom:* Scales dynamically based on inter-hand distance ($w_1$ to $w_2$).
  - *Desktop Wheel / Keys:* Mouse scroll-wheel and keyboard shortcuts (`=` / `-`) provide fallback scaling.

- **Adding a New 3D Hologram Model:**
  1. Write a `make_yourmodel()` builder function in `hologram3d.py` returning `(vertices, edges)` or `(vertices, edges, extra)` with vertices normalized in the range $[-1.0, 1.0]$.
  2. Register the builder in `_BUILDERS`, `MODEL_ORDER`, `MODEL_LABELS`, and `MODEL_COLORS`.
  3. No changes to `main.py` are required; it will automatically appear in the cyclic library!

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