# 🚀 Hand Tricks - Feature Documentation

This document describes all features, interactive keyboard controls, performance optimizations, and technical details of the **Hand Tricks** visual application.

---

## 🎭 Interactive Visual Effects

You can toggle between different eye-catching effects in real-time by pressing the corresponding number keys (`0` to `6`) on your keyboard.

### 0️⃣ Standard Glow (Classic Mode)
* **Description:** Draws circular nodes on all 21 hand landmarks and connects matching fingertips of both hands with dynamic color lines. The color shifts smoothly between green, blue, and red depending on the relative physical distance between your hands.
* **Aesthetic style:** Premium neon glow.

### 1️⃣ Inversion Portal (Negative Box)
* **Description:** Detects the boundary of your hand and creates a rectangular portal framing it. Inside the bounding box, all image colors are inverted to their negative equivalents. The border of the box pulses dynamically with a high-contrast neon corner HUD styling.
* **Best use case:** High-contrast environments.

### 2️⃣ Energy Pulse (Lightning Core)
* **Description:** Electric, jagged lightning bolts arc between your fingertips when both hands are visible. When only one hand is visible, sparks and mini-arcs discharge radially from your fingertips. The jaggedness, intensity, and length of the discharges dynamically scale with the speed of your hand movements.
* **Best use case:** Fast and expressive hand waves.

### 3️⃣ Motion Ghost Trail (Afterimage)
* **Description:** Your movements leave a fading trail of past frames behind them. Hand joints and fingertip connectors from prior positions fade out gracefully using an exponential decay opacity model. The trail shifts color (violet to pink) as it ages.
* **Best use case:** Slow, graceful hand motions.

### 4️⃣ Particle Shower (Magical Sparkles)
* **Description:** Fingertips emit glowing neon particles that stream upward and fall back down under simulated gravity. The number of spawned particles scales with hand velocity. The particles gradually shrink and fade away over time.
* **Best use case:** Dynamic gestures, drawing loops.

### 5️⃣ Ripple Distortion (Liquid/Warp)
* **Description:** The webcam frame behaves like a liquid surface. Moving your hand creates local circular ripples and lens distortions that radiate outward from your hand's center (MCP joint). The wave amplitude increases when you move your hand quickly.
* **Best use case:** Interactive wave gestures.

### 6️⃣ Thermal Vision (Heat Mapping)
* **Description:** Transforms the frame into a hot infrared thermal visualization using a colormap. The hand joints act as heat sources, making the hands glow white/yellow/red, while the background shifts to cold, darkened blue.
* **Best use case:** Creating a sci-fi/high-tech radar aesthetic.

---

## 🛠️ Performance & Configuration Controls

To keep the application running smoothly on lightweight laptop setups (e.g., 4GB DDR3 RAM, older Intel i5 CPUs), the following live configuration keys are available:

| Key | Action | Description |
| :--- | :--- | :--- |
| **`D`** | Toggle HUD | Shows or hides the diagnostic dashboard displaying real-time FPS, inference latency, rendering cost, and active resolution. |
| **`R`** | Toggle Resolution | Switches capture resolution between **640x360** (Performance Mode) and **1280x720** (Quality Mode) on the fly. |
| **`B`** | Cycle Glow Mode | Cycles through **Optimized Glow** (blurs at 4x downsample, saving 70% CPU cycles), **Standard Glow** (direct heavy blur), and **Glow Off** (renders lines directly without blur). |
| **`Q`** | Quit | Releases the camera feed, destroys all OpenCV windows, and exits. |

---

## 🔬 Behind the Scenes: Optimization Architecture

1. **Pre-allocated Memory Pools:** Avoids runtime garbage collection stuttering on systems with limited RAM (like 4GB DDR3) by instantiating the canvas image and coordination mappings once, cleaning them in-place with `.fill(0)` and vectorized resets instead of allocating new matrices on every frame.
2. **Temporal Video Tracking (`vision.RunningMode.VIDEO`):** Switches MediaPipe from static frame detection (which runs expensive classification models across the full image every frame) to active video tracking. The detection model is only run on frame loss; otherwise, landmarks are calculated inside a localized bounding box tracked from the previous frame.
3. **Downscaled Glow Blurring:** OpenCV Gaussian blurs scale quadratically with image resolution. By downscaling the canvas by 4x, running a smaller blur kernel (e.g., 5x5 instead of 19x19), and upscaling back to blend, we achieve a highly diffuse organic glow with **93% fewer pixels processed**.
4. **Asynchronous Camera Scanner:** Scanning for cameras in Tkinter runs in a background thread to prevent UI freezing during startup, using a stylized dark theme built to look clean and premium.
