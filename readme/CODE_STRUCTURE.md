### Recent Additions

The hologram renderer now accepts a quality flag: Studio mode adds masked volume lighting and a projector grid, while Fast mode keeps depth-sorted geometry with lower CPU cost. Clean hand mode suppresses debug and motion-trail skeletons without changing landmark tracking or gesture state.

- `hologram3d.py` — Standalone, dependency-free (numpy + OpenCV only) real-time 3D wireframe engine. Owns three responsibilities:
  1. **Model builders** — `make_cube`, `make_globe`, `make_human`, `make_car`, `make_plane`, `make_building`, `make_pyramid`, `make_atom`. Each returns `(vertices: Nx3 float32 ndarray, edges: list[(i, j)])` (a few also return an `extra` dict for things like emphasized joints/nucleus points). Registered in `_BUILDERS` / `MODEL_ORDER` / `MODEL_LABELS` / `MODEL_COLORS`.
  2. **Math** — `rotate_xy()` applies real rotation matrices (X axis, then Y axis) to the model's vertices; `project()` does perspective projection from 3D model space to 2D screen pixels with depth values for shading/ordering.
  3. **Renderer** — `render_hologram(canvas, model_key, center, rot_x_deg, rot_y_deg, pixel_size, ...)` draws the projected wireframe with depth-based glow shading (painter's algorithm: far edges first, near edges last) and a soft holographic "projector disc" base.
  - Adding a new object = write one more `make_x()` builder and register it in `_BUILDERS`/`MODEL_ORDER`/`MODEL_LABELS`/`MODEL_COLORS` — nothing else in the file needs to change, and `main.py` doesn't need touching either.
- `main.py` integrates `hologram3d` via `draw_hologram_object()`, a thin wrapper that calls `hologram3d.render_hologram()` (falling back to a simple faux-cube renderer, `_draw_fallback_cube()`, only if the module fails to import).
- `ws_server.py` — Simple WebSocket broadcaster that streams latest hand landmarks as JSON to connected clients. Useful for offloading rendering/control to remote 3D renderers or devices.
- UI toggles and state in `main.py` for hiding hand outlines, the 3D hologram overlay, hologram object cycling, and pinch-based digital zoom.

Refinements:

- Hologram grab/drag/rotate/inertia/snap-to-palm state lives in `AppState.cube` (kept as the historical attribute name for the physics dict — position, velocities, damping, snap threshold, `rot_x`/`rot_y`, `scale`, `size`). `AppState.holo_model` stores which object is currently selected (see `hologram3d.MODEL_ORDER`).
- Rotation (`rot_x`/`rot_y`) is stored **unbounded** in degrees (not wrapped to 0–360) so the object can keep spinning continuously past a full turn on either axis without any visible reset/snap.
- Zoom has three independent inputs that all feed the same `AppState.cube['scale']` multiplier: (1) single-hand "pull to zoom" — `AppState.holo_grab_span` tracks the on-screen span of the grabbing hand (wrist→middle-fingertip) frame to frame as a depth proxy while grabbed; (2) two-hand pinch spread, which instead drives `AppState.cube['size']` directly by hand separation; (3) manual keyboard (`=`/`-`) and mouse scroll-wheel input via `mouse_callback()`.
- Clean hand mode suppresses the optional debug skeleton and motion-trail skeletons globally; it does not disable MediaPipe landmarks or any gesture state.

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