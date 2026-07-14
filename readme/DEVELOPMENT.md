## New Interactive Features

When developing or extending the project, note the following new interactive features:

- `O`: Toggle hand outline/lines rendering.
- `M`: Toggle the faux 3D cube overlay (palm anchored). Pinch to grab and move.
- `P`: Toggle pinch zoom behavior.
- `W`: Start/stop the WebSocket landmark broadcaster for remote clients.

These are implemented in `main.py` and the lightweight server is `ws_server.py`.

### Cube Interaction Implementation Notes

- Rotation: Implemented by tracking the index fingertip delta while the cube is grabbed. Horizontal movement maps to `rot_y`, vertical to `rot_x`.
- Scaling: Implemented two modes: two-hand distance driven automatic scaling, and manual keyboard scaling which modifies `cube['scale']` in the runtime state.

### Inertia & Snapping

- When the cube is released it preserves last motion/rotation velocity for a short time and decays using `cube['damping']`.
- When the cube is close to the palm center it gently snaps toward the palm using `cube['snap_speed']` and reduces velocities.


