# 📐 Code Structure & Architecture

This document provides an in-depth overview of the **Hand Tricks** codebase, including class structures, functions, and the main execution flow.

---

## 📁 Project Layout

```
Hand Tricks/
├── main.py                          # Main application entry point
├── hand_landmarker.task             # MediaPipe Hand Landmarker model (binary)
├── requirements.txt                 # Python dependencies
├── README.md                        # Project overview and quick start
├── CHANGELOG.md                     # Version history and bug fixes
├── TROUBLESHOOTING.md               # Common issues and solutions
├── CODE_STRUCTURE.md                # This file
├── LICENSE                          # MIT License
├── .gitignore                       # Git ignore rules
├── .venv/                           # Virtual environment (auto-created)
├── captures/                        # Photo and video output folder (auto-created)
└── readme/
    ├── FEATURES.md                  # Detailed feature descriptions
    └── IDE_SETUP_GUIDE.md           # IDE-specific setup instructions
```

---

## 🏗️ Architecture Overview

The application uses a **single-threaded event loop** model with the following layers:

```
┌─────────────────────────────────────────────┐
│     User Input Layer (Keyboard/Mouse)       │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│     Main Event Loop (while cap.isOpened)    │
│  - Frame capture from camera                │
│  - Hand detection (MediaPipe inference)     │
│  - Effect rendering                         │
│  - UI rendering (HUD, buttons, text)        │
│  - Video output to window & file            │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│   State Management (AppState class)         │
│  - Effect parameters                        │
│  - Particle systems                         │
│  - Recording state                          │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│    Background Systems (Threading)           │
│  - Audio playback (winsound, async)         │
│  - Camera initialization (async scan)       │
└─────────────────────────────────────────────┘
```

---

## 📊 Class & Function Reference

### 🎛️ Core Classes

#### `AppState`
**Purpose:** Encapsulates all mutable application state.

**Location:** Lines 168–222

**Attributes:**
```python
active_effect: int              # Currently selected effect (0-9)
show_hud: bool                  # Diagnostic overlay visibility
w, h: int                       # Frame width and height
glow_mode: int                  # Glow rendering mode (0: Optimized, 1: Standard, 2: Off)
fullscreen: bool                # Fullscreen mode flag

# Velocity tracking for effects
prev_wrists: dict               # {hand_id: (x, y)} - Previous wrist positions
hand_velocities: dict           # {hand_id: velocity} - Computed velocities

# Particle systems (pre-allocated)
ghost_buffer: list              # Motion trail frames
particles: list                 # Shower/falling particles
orbit_particles: list           # Orbit effect particles
digital_chars: list             # Matrix rain characters
goku_particles: list            # Super Saiyan fire particles

# Recording state
trigger_capture: bool           # Flag to save photo
trigger_record: bool            # Flag to toggle recording
is_recording: bool              # Current recording status
video_writer: cv2.VideoWriter   # OpenCV video encoder

# UI state
notification_text: str          # Popup message text
notification_time: float        # Notification expiration time
map_x, map_y: np.ndarray       # Ripple distortion maps (pre-allocated)
```

**Key Methods:**
- `__init__(w, h)` – Initialize all state
- `init_ripple_maps(w, h)` – Pre-allocate ripple distortion coordinate maps
- `set_notification(text)` – Queue a 2-second popup message

---

### 🎮 Main Functions

#### `choose_camera() → int`
**Purpose:** Display camera selection GUI using tkinter.

**Location:** Lines 42–109

**Returns:** Selected camera index (default 0 if none available)

**Process:**
1. Scans for available cameras (indices 0–4)
2. Tests each camera with `VideoCapture.read()`
3. Displays buttons for each working camera
4. Runs in a tkinter GUI with dark theme styling

---

#### `track_hands(landmarks, prev_wrists, w, h) → (dict, dict)`
**Purpose:** Match current hand detections to previous frames for smooth tracking.

**Location:** Lines 224–251

**Parameters:**
- `landmarks` – Current frame hand landmarks from MediaPipe
- `prev_wrists` – Wrist positions from previous frame
- `w, h` – Frame dimensions for normalization

**Returns:**
- `current_wrists` – {hand_id: (x, y)}
- `velocities` – {hand_id: pixel_distance}

**Algorithm:**
1. Extract wrist position for each detected hand
2. Match to closest previous wrist (within 180px threshold)
3. Assign new IDs to unmatched hands
4. Compute velocity as euclidean distance traveled

---

#### `main() → None`
**Purpose:** Main application loop.

**Location:** Lines 318–947

**Flow:**
1. **Initialization (Lines 319–350)**
   - Camera selection
   - Frame resolution setup (640×360 default)
   - MediaPipe HandLandmarker configuration
   - Window and mouse callback setup

2. **Event Loop (Lines 370–942)**
   - Read frame from camera
   - Run hand detection inference
   - Track hand velocities
   - Render active visual effect to canvas
   - Apply glow processing
   - Render UI overlays (HUD, buttons)
   - Save/record on trigger
   - Process keyboard input

3. **Cleanup (Lines 944–947)**
   - Release camera and video writer
   - Close all windows

---

### 🎨 Visual Effect Rendering Functions

#### Effect Routing (Lines 439–765)

Each effect is rendered in a separate `elif` block:

**Effect 0 (Standard Glow)** – Lines 439+ *(implicit, rendered via hand skeleton overlay)*
- Draws distance-based color-shifting lines

**Effect 1 (Inversion Portal)** – Lines 440–462
- Inverts colors within bounding box
- Draws pulsing corner HUD frame

**Effect 2 (Energy Pulse)** – Lines 463–492
- Draws jagged lightning arcs from fingertips
- Scales with hand velocity

**Effect 3 (Motion Ghost Trail)** – Lines 493–524
- Fades prior frame images with exponential decay
- Color shifts from violet to magenta

**Effect 4 (Particle Shower)** – Lines 525–548
- Spawns particles from fingertips
- Simulates gravity and fade

**Effect 5 (Ripple Distortion)** – Lines 549–573
- Pre-computes ripple displacement maps
- Uses `cv2.remap()` for efficient warping

**Effect 6 (Thermal Vision)** – Lines 574–602
- Applies colormap to image
- Adds heat source glow at hand joints

**Effect 7 (Particle Orbit)** – Lines 604–651
- Orbits particles around hand center (MCP joint)
- Radius pulses with hand velocity

**Effect 8 (Digital Rain Aura)** – Lines 653–678
- Spawns matrix-style characters from joints
- Characters drift upward with fade

**Effect 9 (Goku Power Core)** – Lines 680–764
- Golden Super Saiyan aura from all joints
- Kamehameha energy ball when hands close (< 240px)
- Lightning arcs from index fingers
- Synth charging sound

---

### 🔧 Utility Functions

#### `get_dynamic_color(distance, max_distance=1000) → (int, int, int)`
**Purpose:** Compute HSV-to-BGR color based on distance.

**Location:** Lines 111–120

**Algorithm:**
1. Clip distance to [0, max_distance]
2. Map to HSV hue: 140 – 110 * (distance / max_distance)
3. Use full saturation (255) and value (255)
4. Convert HSV → BGR via OpenCV

**Result:** Green (close) → Blue (medium) → Red (far)

---

#### `draw_hud_corners(img, pt1, pt2, color, thickness=2, length=15)`
**Purpose:** Draw four corner brackets (for Inversion Portal effect).

**Location:** Lines 122–137

**Parameters:**
- `img` – Target image array
- `pt1, pt2` – Diagonal corners (top-left, bottom-right)
- `color` – RGB/BGR color tuple
- `thickness` – Line thickness
- `length` – Bracket arm length

---

#### `draw_lightning(img, pt1, pt2, color, thickness=1, segments=5, displace=12)`
**Purpose:** Draw jagged lightning between two points.

**Location:** Lines 139–166

**Algorithm:**
1. Compute line segment count and perpendicular direction
2. For each intermediate point, add random perpendicular displacement
3. Draw line segments with antialiasing

**Used by:** Energy Pulse effect (Effect 2) and Goku Power Core (Effect 9)

---

#### `draw_semi_transparent_rect(img, pt1, pt2, color, alpha)`
**Purpose:** Draw a semi-transparent rectangle (HUD background).

**Location:** Lines 253–262

**Algorithm:**
1. Extract sub-image at coordinates
2. Blend with color using alpha blending
3. Write back to original image

---

### 🔊 Audio Functions (Async, Threading)

#### `play_beep_async(freq, duration)`
**Lines:** 265–271
- Spawns background thread with `winsound.Beep()`
- Non-blocking

#### `play_shutter_sound()`
**Lines:** 273–274
- 1800 Hz beep for photo capture

#### `play_rec_start()`
**Lines:** 276–283
- Two-tone ascending beep sequence for recording start

#### `play_rec_stop()`
**Lines:** 285–292
- Two-tone descending beep sequence for recording stop

#### `play_kamehameha_charge()`
**Lines:** 294–305
- Synth frequency sweep from 120–520 Hz for Goku effect

---

### 🖱️ Event Handlers

#### `mouse_callback(event, x, y, flags, param) → None`
**Purpose:** Handle mouse clicks on UI buttons.

**Location:** Lines 308–316

**Buttons:**
- **Photo Button:** [w–110, 15] to [w–65, 45] → `trigger_capture = True`
- **Record Button:** [w–55, 15] to [w–10, 45] → `trigger_record = True`

---

## 🔄 Main Event Loop Flow

```
┌─────────────────────────────────────────────────┐
│ 1. Read Frame from Camera                       │
│    cap.read() → image, ~30fps @ 360p            │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ 2. Convert & Detect Hands                       │
│    BGR → RGB → MediaPipe inference (~25–35ms)   │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ 3. Track Hand Velocities                        │
│    Match wrists to prev frame, compute distance │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ 4. Render Active Visual Effect                  │
│    Dispatch to effect 0–9 rendering function    │
│    Draw on black canvas                         │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ 5. Apply Glow Processing                        │
│    Mode 0: Downsample → Blur → Upsample (fast)  │
│    Mode 1: Direct blur (standard)               │
│    Mode 2: Skip (off)                           │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ 6. Render HUD & Buttons                         │
│    Draw diagnostic overlay, capture button,     │
│    record indicator, notifications              │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ 7. Handle Photo/Video Capture                   │
│    Write frame to file if triggered             │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ 8. Display Output                               │
│    cv2.imshow() → Screen                        │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ 9. Process Keyboard Input                       │
│    0–9: Effect switch                           │
│    R: Resolution toggle                         │
│    B: Glow mode cycle                           │
│    D: HUD toggle                                │
│    F: Fullscreen                                │
│    C: Capture photo                             │
│    V: Record video                              │
│    Q: Quit                                      │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ 10. Update FPS Counter                          │
│     Recalculate if ≥ 0.5 seconds elapsed        │
└─────────────────┬───────────────────────────────┘
                  │
                  └─────────────────┬──────────────┐
                                    │              │
                         Loop until Q pressed    Exit
```

---

## ⚡ Performance Optimizations

### 1. Downscaled Gaussian Blur (Mode 0)
- **Concept:** Blur at 1/4 resolution, then upsample
- **Speedup:** ~3.0x vs. direct blur
- **Trade-off:** Slightly softer appearance (imperceptible at 30+ FPS)

### 2. Pre-allocated Memory
- **Ripple maps:** Pre-computed X/Y displacement grids
- **Canvas buffer:** Reused frame array (not reallocated each iteration)
- **Particle lists:** Trimmed to max size (no unbounded growth)

### 3. Video Mode Tracking
- MediaPipe uses `RunningMode.VIDEO` for continuous tracking
- Skips expensive full-frame detection passes after first frame
- Assumes hands don't appear/disappear abruptly

### 4. Temporal Hand Tracking
- Matches current wrists to previous frame wrists
- Assigns persistent IDs for smooth velocity calculations
- Threshold of 180px prevents false matches

### 5. Selective Effect Rendering
- Only active effect renders each frame
- No unused particle systems update
- Joint overlays skip rendering in Thermal Vision (Effect 6)

---

## 🔐 State Management

### Resolution Changes
When resolution is toggled (press R):
1. Release and reinitialize camera
2. Update `state.w` and `state.h`
3. Reinitialize ripple maps
4. Clear all particle systems
5. Force stop recording if active

### Recording Lifecycle
```
trigger_record = True
    ↓
is_recording = NOT is_recording
    ↓
[if now recording]
    Create filename with timestamp
    Initialize cv2.VideoWriter (XVID codec)
    Set notification
    Play start sound
    ↓
[else]
    Release video_writer
    Set notification
    Play stop sound
```

### Particle System Limits
- **Ghost trail:** Unbounded (fades naturally)
- **Shower particles:** Auto-capped (new_parts[-150:])
- **Orbit particles:** Auto-capped (new_parts[-150:])
- **Digital chars:** Auto-capped (new_chars[-120:])
- **Goku particles:** Auto-capped (new_parts[-200:])

---

## 🐛 Known Technical Debt

1. **Single-threaded event loop:** Keyboard input can lag if inference is slow
2. **No error handling in effect loops:** Malformed landmarks could crash (currently rare)
3. **Hardcoded button coordinates:** Not responsive to window resizing
4. **No gesture recognition:** All effects are continuous, not pose-triggered

---

## 🚀 Future Architecture Improvements

- [ ] Multi-threaded inference (separate thread for MediaPipe)
- [ ] Plugin system for custom effects
- [ ] Configuration file (YAML/JSON) for effect presets
- [ ] WebRTC streaming for remote display
- [ ] GPU acceleration (CUDA/OpenCL) for glow processing
- [ ] Gesture classification (thumbs up, peace sign, etc.)

---

## 📚 Further Reading

- [MediaPipe Hand Landmarker Docs](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker)
- [OpenCV Documentation](https://docs.opencv.org/)
- [NumPy Documentation](https://numpy.org/doc/)

See also: [FEATURES.md](readme/FEATURES.md), [TROUBLESHOOTING.md](TROUBLESHOOTING.md), [CHANGELOG.md](CHANGELOG.md)
