## New Interactive Features

When developing or extending the project, note the following new interactive features:

- `O`: Toggle hand outline/lines rendering.
- `M`: Toggle the holographic 3D object overlay (palm anchored). Pinch to grab, rotate 360 on X/Y, and zoom in/out.
- `N`: Cycle the active hologram object (`Shift+N` for the previous). See `hologram3d.MODEL_ORDER`.
- `P`: Toggle pinch zoom behavior.
- `W`: Start/stop the WebSocket landmark broadcaster for remote clients.

These are implemented in `main.py` (gesture/state handling and rendering call-out) and `hologram3d.py` (the 3D model builders, rotation math, projection, and wireframe renderer); the lightweight server is `ws_server.py`.

### Hologram Interaction Implementation Notes

- Rotation: Implemented by tracking the index fingertip delta while the hologram is grabbed. Horizontal movement maps to `rot_y`, vertical to `rot_x`. Both are stored **unbounded** (not wrapped to 0-360) in `AppState.cube['rot_x'] / ['rot_y']`, so the object can keep spinning continuously past a full turn on either axis.
- Zoom: Implemented three ways, all feeding `cube['scale']` / `cube['size']`: (1) single-hand pull-to-zoom, which compares the current on-screen span of the grabbing hand (wrist to middle-fingertip) against `AppState.holo_grab_span` from the previous frame; (2) two-hand distance driven automatic scaling; (3) manual keyboard (`=`/`-`) and mouse scroll-wheel scaling via `mouse_callback()`.
- Rendering: `draw_hologram_object()` in `main.py` calls `hologram3d.render_hologram()`, which rotates the model's vertices with `rotate_xy()`, projects them with `project()`, and draws depth-shaded wireframe edges + glowing vertex nodes onto the canvas.
- Adding a new object: write a `make_x()` builder in `hologram3d.py` returning `(vertices, edges)` (or `(vertices, edges, extra)`), then register it in `_BUILDERS`, `MODEL_ORDER`, `MODEL_LABELS`, and `MODEL_COLORS`. No changes to `main.py` are required.

### Inertia & Snapping

- When the hologram is released it preserves last motion/rotation velocity for a short time and decays using `cube['damping']`.
- When the hologram is close to the palm center it gently snaps toward the palm using `cube['snap_speed']` and reduces velocities.

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