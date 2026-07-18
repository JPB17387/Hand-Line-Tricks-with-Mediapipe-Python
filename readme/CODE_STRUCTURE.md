### Recent Additions

- `ws_server.py` — Simple WebSocket broadcaster that streams latest hand landmarks as JSON to connected clients. Useful for offloading rendering/control to remote 3D renderers or devices.
- New UI toggles and state in `main.py` for hiding hand outlines, enabling a faux 3D cube, and pinch-based digital zoom.

Refinements:

- Cube behavior includes inertia/damping and snap-to-palm logic; cube physics state (velocities, damping, snap threshold) lives in `AppState.cube`.
- Palm-line suppression logic uses `PALM_INDICES` to optionally skip drawing palm skeletal lines when cube or zoom is active.

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