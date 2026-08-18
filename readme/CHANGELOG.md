## Unreleased

- **New:** Replaced the faux 3D cube with a full holographic 3D object engine (`hologram3d.py`) — real rotation matrices + perspective projection, depth-based glow shading, and a holographic projector-disc base.
- **New:** 8 selectable holographic objects — Cube, Globe, Human, Car, Plane, Building, Pyramid, and Atom. Cycle with `N` (next) / `Shift+N` (previous).
- **New:** Free 360° rotation on both the X and Y axes at once, unbounded (the hologram can keep spinning continuously past a full turn rather than resetting at 360°).
- **New:** Grab-and-zoom — pull your grabbing hand toward/away from the camera to zoom the hologram in/out (single-hand "pull to zoom", estimated from the hand's on-screen size), in addition to the existing two-hand pinch-spread zoom. Mouse scroll-wheel also zooms the hologram.
- Added interactive toggles: hide hand outlines (`O`), 3D hologram overlay (`M`), pinch zoom toggle (`P`).
- Added `ws_server.py` for broadcasting landmarks to remote clients; start/stop with `W` key.
- Updated documentation (README, FEATURES, CODE_STRUCTURE, PROJECT_SUMMARY, DOCUMENTATION_INDEX) to describe the hologram system and its controls.
- Refinements: hologram inertia/damping, snap-to-palm, depth-shaded wireframe rendering; palm line suppression when the hologram/zoom is active.


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