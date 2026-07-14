## Notes on New Features

- If the WebSocket streamer fails to start, ensure `websockets` is installed (`pip install websockets`).
- The faux 3D cube and pinch zoom are display-only features; recording still saves the full-resolution unzoomed frame.

# 🔧 Troubleshooting Guide

This guide helps you resolve common issues when running the **Hand Tricks** application.

---

## 🚨 Installation & Setup Issues

### ❌ "ModuleNotFoundError: No module named 'mediapipe'"

**Cause:** The virtual environment is not activated, or MediaPipe was not installed.

**Solution:**
1. Activate your virtual environment:
   ```powershell
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   ```
   ```cmd
   # Windows Command Prompt
   .venv\Scripts\activate.bat
   ```
   ```bash
   # macOS/Linux
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Verify installation:
   ```bash
   python -c "import mediapipe; print('MediaPipe OK')"
   ```

---

### ❌ "ERROR: Failed to install mediapipe" (Python 3.13+)

**Cause:** MediaPipe only supports Python 3.8 – 3.12. Python 3.13 and 3.14 are not compatible.

**Solution:**
1. Check your Python version:
   ```bash
   python --version
   ```
2. If you have Python 3.13+, install Python 3.12:
   ```powershell
   # Windows (using winget)
   winget install Python.Python.3.12
   ```
   Or download from [python.org/downloads](https://www.python.org/downloads/release/python-3129/)

3. Create a new virtual environment with Python 3.12:
   ```powershell
   "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python312\python.exe" -m venv .venv
   ```

---

### ❌ "No cameras found!"

**Cause:** The application cannot detect any camera devices.

**Solution:**
1. Check if your camera is physically connected and powered on.
2. Verify camera isn't in use by another application (Zoom, Teams, etc.).
3. Check Device Manager (Windows) for disabled camera drivers.
4. Restart your computer and try again.
5. Update your camera driver from the manufacturer's website.

---

## 🎥 Camera & Detection Issues

### ❌ Application freezes after camera selection

**Cause:** Camera initialization is slow, or the camera is incompatible.

**Solution:**
1. Wait 5-10 seconds for initialization.
2. If it still freezes, press **Ctrl+C** to force exit.
3. Check if another application has exclusive access to the camera.
4. Try a different camera if available.
5. Restart the application.

---

### ❌ Hand detection not working or very unreliable

**Cause:** Poor lighting, low resolution, or MediaPipe model not loading.

**Solution:**
1. **Improve lighting:**
   - Ensure good natural or artificial lighting.
   - Avoid backlighting or harsh shadows on hands.
   - The model works best in well-lit environments.

2. **Adjust hand detection confidence thresholds** (in main.py, lines 346-348):
   ```python
   min_hand_detection_confidence=0.55,      # Lower to 0.4 for harder detection
   min_hand_presence_confidence=0.55,       # Lower to 0.4 for harder presence
   min_tracking_confidence=0.6,             # Lower to 0.5 for harder tracking
   ```
   
3. **Verify the model file exists:**
   ```bash
   ls hand_landmarker.task
   # or on Windows:
   dir hand_landmarker.task
   ```

4. **Try 720p resolution:**
   - Press **R** to toggle to 720p mode.
   - Higher resolution may improve detection accuracy at the cost of performance.

---

### ❌ FPS is very low (< 10 FPS)

**Cause:** Hardware too slow, resolution too high, or glow mode expensive.

**Solution:**
1. **Switch to 360p resolution:**
   - Press **R** to toggle to 360p mode.

2. **Use optimized glow mode:**
   - Press **B** to cycle through glow modes.
   - Mode 0 (Downsampled Blur) is fastest.

3. **Disable diagnostic HUD:**
   - Press **D** to hide the HUD overlay.
   - This saves a small amount of rendering time.

4. **Use a simpler effect:**
   - Try effect 0 (Standard Glow) or effect 1 (Inversion Portal).
   - Complex effects like 4 (Particle Shower) and 9 (Goku Power Core) are more demanding.

5. **Close background applications:**
   - Close Chrome, Zoom, Discord, etc. to free up CPU/GPU.

6. **Check system resources:**
   - Open Task Manager (Windows) → Performance tab.
   - If CPU/GPU is already maxed out, hardware may be insufficient.

---

## 🎬 Photo & Video Capture Issues

### ❌ Photos save but can't be opened

**Cause:** The `captures/` folder may not exist, or the image file is corrupted.

**Solution:**
1. Check if the folder exists:
   ```bash
   ls captures/
   # or on Windows:
   dir captures
   ```

2. If missing, create it manually:
   ```bash
   mkdir captures
   ```

3. Try a different image format by editing main.py, line 861:
   ```python
   filename = f"captures/capture_{timestamp}.jpg"  # Use .jpg instead of .png
   ```

---

### ❌ Video recording stops abruptly or produces unplayable files

**Cause:** Insufficient disk space, codec issues, or camera resolution changed during recording.

**Solution:**
1. **Ensure sufficient disk space:**
   - Check that your drive has at least 500 MB free.
   - 1-minute video at 720p ≈ 80-120 MB.

2. **Don't change resolution while recording:**
   - Recording automatically stops if you press **R** to toggle resolution.
   - The application prints: "Recording Stopped (Resolution Changed)"

3. **Check codec support:**
   - The project uses XVID codec.
   - If videos don't play, install K-Lite Codec Pack on Windows.
   - Download: [codec.karagarga.in](https://codec.karagarga.in/)

4. **Try manual codec selection** (main.py, line 872):
   ```python
   # Try alternative codecs:
   fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # Motion JPEG
   # or
   fourcc = cv2.VideoWriter_fourcc(*'H264')  # H.264 (if available)
   ```

---

## 🔊 Audio Issues

### ❌ No sound during capture/recording on Windows

**Cause:** Winsound module disabled or audio device muted.

**Solution:**
1. Check Windows volume levels (bottom-right system tray).
2. Unmute the speaker output.
3. Verify the audio device is not muted in Sound Settings.
4. The beeps use the system speaker; ensure it's enabled.

**Note:** On macOS/Linux, audio is intentionally skipped (no errors will appear).

---

### ❌ No sound on macOS/Linux

**Cause:** The `winsound` module is Windows-only.

**Solution:**
This is expected behavior. The sound effects are wrapped in try/except blocks and fail silently on non-Windows systems. No action needed—the application continues to work normally without sound.

---

## 🖱️ Input & Controls Issues

### ❌ Keyboard controls not responding

**Cause:** The OpenCV window may not be in focus, or key events are buffered.

**Solution:**
1. Click on the OpenCV window to ensure it has focus.
2. Hold the key for 1 second (key events require the window to be active).
3. If stuck, press **Q** to quit and restart.

---

### ❌ Mouse clicks on buttons don't register

**Cause:** Button coordinates may not align with actual screen positions due to window scaling.

**Solution:**
1. Use keyboard shortcuts instead:
   - **C** for photo capture
   - **V** for video recording
2. Verify button hitboxes in main.py:
   ```python
   # Photo button: [w - 110, 15] to [w - 65, 45]
   # Video button: [w - 55, 15] to [w - 10, 45]
   ```
3. Adjust coordinates if your window is scaled.

---

## 💾 File & Path Issues

### ❌ "FileNotFoundError: hand_landmarker.task"

**Cause:** The MediaPipe model file is missing.

**Solution:**
1. Verify the file exists in the project root:
   ```bash
   ls hand_landmarker.task
   ```

2. If missing, download it:
   - Visit [MediaPipe Models](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker/index#get_started)
   - Download `hand_landmarker.task`
   - Place it in the project root directory (same folder as `main.py`)

3. Alternatively, update the path in main.py, line 342:
   ```python
   model_asset_path='path/to/your/hand_landmarker.task'
   ```

---

### ❌ "PermissionError" when saving photos/videos

**Cause:** The `captures/` folder lacks write permissions.

**Solution:**
1. Check folder permissions:
   ```bash
   ls -ld captures  # macOS/Linux
   ```

2. Grant write permissions:
   ```bash
   chmod 755 captures  # macOS/Linux
   ```

3. On Windows, right-click `captures/` → Properties → Security → Edit → Allow "Full Control" for your user.

---

## 🌐 Performance Optimization Tips

### For Low-End Hardware (4GB RAM, i5 2nd gen, integrated graphics)

1. **Always use 360p resolution** (press **R**)
2. **Use optimized glow** (press **B** until "Downsampled Blur" shows)
3. **Avoid effects 4, 8, and 9** (particle-heavy)
4. **Enable diagnostic HUD** (press **D**) to monitor FPS in real-time
5. **Close unnecessary background processes**

### For High-End Hardware (16GB+ RAM, i7/i9, dedicated GPU)

1. Use 720p resolution for best visual quality
2. Use standard glow for premium appearance
3. All effects run smoothly; choose based on aesthetic preference
4. Consider enabling fullscreen mode (**F**) for immersive demos

---

## 📞 Getting More Help

If none of these solutions work:

1. **Check the main README.md** for setup instructions.
2. **Review FEATURES.md** for effect descriptions and use cases.
3. **Read IDE_SETUP_GUIDE.md** for IDE-specific instructions.
4. **Enable the diagnostic HUD** (press **D**) to check FPS and inference times.

For persistent issues, provide:
- Python version: `python --version`
- OS: Windows/macOS/Linux
- OpenCV version: `python -c "import cv2; print(cv2.__version__)"`
- A screenshot of the error
- Steps to reproduce

---

## 🎓 Understanding Performance

The application uses several optimization techniques:

- **Downscaled Gaussian Blur (Glow Mode 0):** ~3.0x faster than direct blur
- **Pre-allocated Memory Pools:** Eliminates garbage collection stutters
- **Video Mode Landmark Tracking:** Prevents full-frame detection bottlenecks
- **Temporal Hand Tracking:** Smooth velocity calculations without visual jitter

See [CHANGELOG.md](CHANGELOG.md) for detailed performance metrics.
