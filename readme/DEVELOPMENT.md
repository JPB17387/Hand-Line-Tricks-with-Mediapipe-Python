# 👨‍💻 Development Guide

This guide is for developers who want to contribute to, extend, or customize the **Hand Tricks** project.

---

## 🏗️ Setting Up a Development Environment

### Prerequisites

- **Python 3.8–3.12** (not 3.13+)
- **Git** for version control
- A code editor: VS Code, PyCharm, or similar

### 1. Clone the Repository

```bash
git clone https://github.com/JPB17387/Hand-Line-Tricks-with-Mediapipe-Python.git
cd "Hand Tricks"
```

### 2. Create & Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 3. Install Development Dependencies

```bash
pip install -r requirements.txt
pip install pytest pylint black  # Optional: testing and linting tools
```

### 4. Verify Installation

```bash
python main.py
```

---

## 📝 Code Style Guidelines

### Naming Conventions

- **Variables & Functions:** `snake_case`
  ```python
  def draw_hand_skeleton():
      pass
  
  prev_wrists = {}
  ```

- **Classes:** `PascalCase`
  ```python
  class AppState:
      pass
  ```

- **Constants:** `UPPER_SNAKE_CASE`
  ```python
  FINGER_TIPS = [4, 8, 12, 16, 20]
  MAX_PARTICLES = 200
  ```

### Comments & Documentation

- **Only comment non-obvious code:** Avoid stating the obvious.
  ```python
  # ✓ Good: Explains why
  # Threshold of 180px prevents false hand matches across frames
  if dist < min_dist and dist < 180:
  
  # ✗ Avoid: States the obvious
  # Check if distance is less than 180
  if dist < 180:
  ```

- **Function docstrings:** Use clear, concise descriptions.
  ```python
  def track_hands(landmarks, prev_wrists, w, h):
      """Match current hand detections to previous frame for smooth tracking.
      
      Args:
          landmarks: Current frame hand landmarks from MediaPipe.
          prev_wrists: Wrist positions from previous frame.
          w, h: Frame dimensions for normalization.
      
      Returns:
          Tuple of (current_wrists, velocities) dicts.
      """
  ```

### Code Formatting

- **Line length:** Keep to ~100 characters (soft limit)
- **Indentation:** 4 spaces (no tabs)
- **Imports:** Sort at the top (stdlib, third-party, local)
  ```python
  import cv2
  import mediapipe as mp
  import numpy as np
  
  from mediapipe.tasks import python
  from mediapipe.tasks.python import vision
  ```

---

## 🎨 Adding a New Visual Effect

### Step 1: Plan Your Effect

1. Choose an available effect number (0–9 are taken)
2. Decide if it uses particle systems, distortions, or overlays
3. Estimate CPU/GPU impact

### Step 2: Add Effect to `EFFECT_NAMES`

**Location:** Line 29–40 in `main.py`

```python
EFFECT_NAMES = {
    ...
    9: "Goku Power Core",
    10: "Your New Effect Name"  # ← Add here
}
```

### Step 3: Add Rendering Logic

**Location:** Effect rendering section (Lines 439–765 in `main.py`)

Add your effect in the appropriate `elif` block:

```python
elif state.active_effect == 10 and results.hand_landmarks:
    # Your effect code here
    for hand in results.hand_landmarks:
        for joint in hand:
            x = int(joint.x * state.w)
            y = int(joint.y * state.h)
            
            # Draw your visual effect
            cv2.circle(canvas, (x, y), radius=5, color=(255, 0, 0), thickness=-1)
```

### Step 3a: (Optional) Pre-allocate State for Performance

If your effect uses particles, initialize storage in `AppState.__init__()`:

**Location:** Lines 168–222

```python
class AppState:
    def __init__(self, w, h):
        # ... existing code ...
        self.your_effect_particles = []  # ← Add here
```

### Step 3b: (Optional) Add State Cleanup on Resolution Change

**Location:** Lines 375–387 and 923–930 (in main event loop)

Add cleanup when resolution changes:

```python
state.your_effect_particles.clear()  # ← Add alongside other clears
```

### Step 4: Test Your Effect

```bash
python main.py
# Press your effect number key to test
# Press D to see FPS impact via the diagnostic HUD
# Press R to test at both 360p and 720p
```

### Step 5: Optimize Performance

- Use pre-allocated arrays instead of list comprehensions in tight loops
- Trim particle lists with slicing: `particles = particles[-MAX_SIZE:]`
- Test on low-end hardware (check FPS via diagnostic HUD)
- Profile with [line_profiler](https://github.com/pyflame/py-spy) if needed

### Example: Simple Gradient Ring Effect

```python
elif state.active_effect == 10 and results.hand_landmarks:
    for hand in results.hand_landmarks:
        cx = int(hand[9].x * state.w)  # Middle finger MCP
        cy = int(hand[9].y * state.h)
        
        # Draw concentric rings
        for i in range(1, 6):
            radius = 20 * i
            alpha = 255 - (i * 40)  # Fade outer rings
            color = (100 + i * 30, 150, 255 - i * 30)
            cv2.circle(canvas, (cx, cy), radius, color, 1, cv2.LINE_AA)
```

---

## 🔧 Modifying Existing Effects

### Finding Your Effect

Use grep to locate effect code:

```bash
grep -n "state.active_effect == 5" main.py
# Output: Line 549 onwards contains Effect 5 (Ripple Distortion)
```

### Common Modifications

#### Change Color Scheme

**Effect 2 (Energy Pulse) Lightning Color:**
```python
# Line ~475
draw_lightning(canvas, pt1, pt2, color=(255, 100, 50), thickness=2)  # Orange-ish
```

#### Adjust Particle Count

**Effect 4 (Particle Shower):**
```python
# Line ~526–536: Increase spawn rate
if len(state.particles) < 300:  # ← Change 150 to 300 for more particles
    for _ in range(15):  # ← Change spawn count
```

#### Modify Animation Speed

**Effect 3 (Motion Ghost Trail):**
```python
# Line ~510: Adjust fade rate
d_life -= 0.05  # ← Increase for faster fade, decrease for longer trail
```

---

## 🐛 Debugging Tips

### 1. Enable Diagnostic HUD

Press **D** during runtime to see:
- Current effect name
- FPS and inference time
- Glow processing time
- Resolution and delegate info

### 2. Print Debug Info

```python
# Add to main event loop (around line 800)
print(f"Frame {fps_frame_count}, Hands: {num_detected}, Effect: {state.active_effect}")
```

### 3. Use Conditional Breakpoints (with VSCode/PyCharm)

```python
if state.active_effect == 5:  # Only break on Effect 5
    breakpoint()  # VSCode/PyCharm stops here
```

### 4. Visualize Hand Landmarks

Add a temporary overlay to see raw landmark positions:

```python
if results.hand_landmarks:
    for hand in results.hand_landmarks:
        for i, lm in enumerate(hand):
            x, y = int(lm.x * state.w), int(lm.y * state.h)
            cv2.circle(canvas, (x, y), 3, (0, 255, 255), -1)
            cv2.putText(canvas, str(i), (x + 5, y - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
```

---

## 🚀 Performance Profiling

### Using `cProfile` for CPU Profiling

```python
# At the end of main()
import cProfile
cProfile.run('main()', sort='cumtime')
```

Run and redirect to file:
```bash
python -m cProfile -o profile.prof main.py
# After exit, analyze:
python -c "import pstats; p = pstats.Stats('profile.prof'); p.sort_stats('cumtime').print_stats(20)"
```

### Checking FPS Impact

1. Enable diagnostic HUD (press **D**)
2. Switch to your effect (press effect number)
3. Monitor "Effect/Blur: X.X / Y.Y ms" line
4. Each frame should be < 50ms total (30 FPS) at 360p

### Memory Usage

```python
import tracemalloc
tracemalloc.start()

# ... your code ...

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.1f}MB; Peak: {peak / 1024 / 1024:.1f}MB")
```

---

## 🧪 Testing

### Manual Testing Checklist

- [ ] **Startup:** Camera selection, hand detection
- [ ] **All Effects:** 0–9 switch without crashes
- [ ] **Resolution Toggle:** Press R, verify smooth transition
- [ ] **Glow Modes:** Press B, test all 3 modes
- [ ] **Photo Capture:** Press C, verify image saves
- [ ] **Video Recording:** Press V, record 10 seconds, verify video plays
- [ ] **Fullscreen:** Press F, verify scaling
- [ ] **HUD Toggle:** Press D, verify overlay on/off
- [ ] **Exit:** Press Q, verify clean shutdown

### Unit Testing (Optional)

Create `test_hand_tricks.py`:

```python
import unittest
from main import get_dynamic_color, draw_hud_corners

class TestUtilityFunctions(unittest.TestCase):
    def test_get_dynamic_color_range(self):
        color = get_dynamic_color(500, max_distance=1000)
        assert all(0 <= c <= 255 for c in color), "Color values should be 0–255"
    
    def test_get_dynamic_color_boundary(self):
        color_near = get_dynamic_color(0, max_distance=1000)
        color_far = get_dynamic_color(1000, max_distance=1000)
        assert color_near != color_far, "Near and far should have different colors"

if __name__ == '__main__':
    unittest.main()
```

Run with:
```bash
python -m pytest test_hand_tricks.py -v
```

---

## 🔗 Dependency Updates

### Check for Updates

```bash
pip list --outdated
```

### Safe Update

Test before committing:
```bash
pip install --upgrade opencv-python mediapipe numpy
python main.py  # Verify no breaking changes
```

### Known Version Constraints

- **Python:** 3.8 – 3.12 (MediaPipe requirement)
- **MediaPipe:** Latest (compatible with above Python versions)
- **OpenCV:** 4.5+ recommended
- **NumPy:** 1.20+

---

## 📦 Contributing Changes

### Before Submitting a PR

1. **Format code** with Black:
   ```bash
   pip install black
   black main.py
   ```

2. **Lint** with Pylint:
   ```bash
   pip install pylint
   pylint main.py --disable=C0111  # Disable missing-docstring for private functions
   ```

3. **Test on multiple resolutions:**
   - 360p (low-end)
   - 720p (high-end)

4. **Verify FPS:**
   - Should maintain 30+ FPS at 360p
   - Should maintain 18+ FPS at 720p
   - With Optimized Glow (Mode 0)

### Commit Message Format

```
[TYPE] Brief description

Longer explanation if needed.

Type: fix, feat, docs, refactor, perf
```

Examples:
```
[fix] Correct "RECING" typo in recording indicator

[feat] Add new particle orbit effect (#10)

[perf] Optimize ripple distortion with pre-allocated maps
```

---

## 📚 Resources

- **MediaPipe Docs:** https://developers.google.com/mediapipe/
- **OpenCV Docs:** https://docs.opencv.org/
- **NumPy Docs:** https://numpy.org/doc/
- **Python Performance:** https://wiki.python.org/moin/PythonSpeed/PerformanceTips

---

## 🙏 Getting Help

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Review [CODE_STRUCTURE.md](CODE_STRUCTURE.md) for architecture details
- Search existing GitHub issues
- Ask in discussions or open a new issue with:
  - Your Python version
  - OS (Windows/macOS/Linux)
  - Hardware specs
  - Steps to reproduce
  - Error messages or logs

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the same MIT License as the project.

---

**Happy coding! 🚀**
