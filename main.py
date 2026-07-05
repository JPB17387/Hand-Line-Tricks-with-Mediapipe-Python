import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import math
import time
import tkinter as tk
from tkinter import ttk
import threading
import random

# Indices corresponding to MediaPipe Hand landmarks
FINGER_TIPS = [4, 8, 12, 16, 20]     # THUMB_TIP, INDEX_FINGER_TIP, etc.
FINGER_JOINTS = [3, 7, 11, 15, 19]   # THUMB_IP, INDEX_FINGER_DIP, etc.

# Internal skeletal connections within a single hand
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),      # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),      # Index
    (5, 9), (9, 10), (10, 11), (11, 12), # Middle
    (9, 13), (13, 14), (14, 15), (15, 16), # Ring
    (13, 17), (17, 18), (18, 19), (19, 20), # Pinky
    (0, 17)                              # Palm base
]

EFFECT_NAMES = {
    0: "Standard Glow",
    1: "Inversion Portal",
    2: "Energy Pulse",
    3: "Motion Ghost Trail",
    4: "Particle Shower",
    5: "Ripple Distortion",
    6: "Thermal Vision",
    7: "Particle Orbit",
    8: "Digital Rain Aura"
}

def choose_camera():
    selected_camera = [0]
    
    root = tk.Tk()
    root.title("Antigravity - Select Camera")
    root.geometry("380x350")
    root.configure(bg="#121214")
    # center window
    root.eval('tk::PlaceWindow . center')
    
    # Custom dark styling
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure(".", background="#121214", foreground="#FFFFFF")
    style.configure("TLabel", background="#121214", foreground="#E4E4E7", font=("Segoe UI", 11))
    style.configure("Title.TLabel", background="#121214", foreground="#6366F1", font=("Segoe UI", 14, "bold"))
    style.configure("TFrame", background="#121214")
    style.configure("TButton", background="#312E81", foreground="#FFFFFF", borderwidth=0, focuscolor="none", font=("Segoe UI", 10, "bold"))
    style.map("TButton", 
              background=[("active", "#4338CA"), ("pressed", "#3730A3")],
              foreground=[("active", "#FFFFFF")])
    
    lbl_title = ttk.Label(root, text="Hand Tricks Launcher", style="Title.TLabel")
    lbl_title.pack(pady=(25, 10))
    
    lbl = ttk.Label(root, text="Scanning for available cameras...", font=("Segoe UI", 10))
    lbl.pack(pady=10)
    
    btn_frame = ttk.Frame(root)
    btn_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
    
    def on_select(idx):
        selected_camera[0] = idx
        root.destroy()
        
    def scan_cams():
        available = []
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available.append(i)
                cap.release()
            else:
                cap.release()
        root.after(0, build_ui, available)
        
    def build_ui(available):
        lbl.config(text="Select the camera to use:")
        if not available:
            lbl.config(text="No cameras found! Trying default (Camera 0)...")
            btn = ttk.Button(btn_frame, text="Continue (Camera 0)", command=lambda: on_select(0))
            btn.pack(pady=10, fill=tk.X)
            return
            
        for idx in available:
            name = f"Camera {idx}"
            if idx == 0:
                name += " (Built-in Camera)"
            else:
                name += " (Webcam / External)"
            btn = ttk.Button(btn_frame, text=name, command=lambda i=idx: on_select(i))
            btn.pack(pady=5, fill=tk.X)
            
    threading.Thread(target=scan_cams, daemon=True).start()
    root.protocol("WM_DELETE_WINDOW", lambda: on_select(0))
    root.mainloop()
    return selected_camera[0]

def get_dynamic_color(distance, max_distance=1000):
    clipped_dist = max(0, min(distance, max_distance))
    hue = int(140 - (clipped_dist / max_distance) * 110)
    hue = max(0, min(hue, 179))
    
    hsv_color = np.uint8([[[hue, 255, 255]]])
    bgr_color = cv2.cvtColor(hsv_color, cv2.COLOR_HSV2BGR)
    
    color = bgr_color[0][0]
    return (int(color[0]), int(color[1]), int(color[2]))

def draw_hud_corners(img, pt1, pt2, color, thickness=2, length=15):
    x1, y1 = pt1
    x2, y2 = pt2
    # Ensure thickness parameter is strictly greater than 0 to avoid OpenCV errors
    thickness = max(1, thickness)
    # Top-left corner
    cv2.line(img, (x1, y1), (x1 + length, y1), color, thickness)
    cv2.line(img, (x1, y1), (x1, y1 + length), color, thickness)
    # Top-right corner
    cv2.line(img, (x2, y1), (x2 - length, y1), color, thickness)
    cv2.line(img, (x2, y1), (x2, y1 + length), color, thickness)
    # Bottom-left corner
    cv2.line(img, (x1, y2), (x1 + length, y2), color, thickness)
    cv2.line(img, (x1, y2), (x1, y2 - length), color, thickness)
    # Bottom-right corner
    cv2.line(img, (x2, y2), (x2 - length, y2), color, thickness)
    cv2.line(img, (x2, y2), (x2, y2 - length), color, thickness)

def draw_lightning(img, pt1, pt2, color, thickness=1, segments=5, displace=12):
    x1, y1 = pt1
    x2, y2 = pt2
    dx = x2 - x1
    dy = y2 - y1
    dist = math.hypot(dx, dy)
    if dist < 5:
        return
        
    points = [pt1]
    nx = -dy / dist
    ny = dx / dist
    
    for i in range(1, segments):
        t = i / segments
        px = x1 + dx * t
        py = y1 + dy * t
        
        # Add jagged offset perpendicular to line
        disp = np.random.uniform(-displace, displace)
        px += nx * disp
        py += ny * disp
        
        points.append((int(px), int(py)))
        
    points.append(pt2)
    
    for i in range(len(points) - 1):
        cv2.line(img, points[i], points[i+1], color, thickness, cv2.LINE_AA)

class AppState:
    def __init__(self, w, h):
        self.active_effect = 0  # 0 to 8
        self.show_hud = True
        self.w = w
        self.h = h
        self.glow_mode = 0  # 0: Optimized, 1: Standard, 2: Off
        
        # Velocity Tracking
        self.prev_wrists = {}  # {hand_idx: (x, y)}
        self.hand_velocities = {}  # {hand_idx: float}
        
        # Ghost Trail
        self.ghost_buffer = []  # list of frame hands
        
        # Particle System
        self.particles = []
        
        # Particle Orbit System
        self.orbit_particles = []  # list of [angle, radius, speed, life, color_offset]
        
        # Digital Rain Aura Characters
        self.digital_chars = []  # list of [x, y, char, speed, life, color_offset]
        
        # Ripple Distortion Pre-allocated Maps
        self.map_x = None
        self.map_y = None
        self.init_ripple_maps(w, h)
        
    def init_ripple_maps(self, w, h):
        self.w = w
        self.h = h
        self.map_x = np.zeros((h, w), dtype=np.float32)
        self.map_y = np.zeros((h, w), dtype=np.float32)
        for y in range(h):
            self.map_x[y, :] = np.arange(w, dtype=np.float32)
        for x in range(w):
            self.map_y[:, x] = np.arange(h, dtype=np.float32)

def track_hands(landmarks, prev_wrists, w, h):
    current_wrists = {}
    velocities = {}
    
    for i, hand in enumerate(landmarks):
        wx = int(hand[0].x * w)
        wy = int(hand[0].y * h)
        
        # Match with closest wrist from last frame
        best_id = None
        min_dist = float('inf')
        for prev_id, prev_loc in prev_wrists.items():
            dist = math.hypot(wx - prev_loc[0], wy - prev_loc[1])
            if dist < min_dist and dist < 180:
                min_dist = dist
                best_id = prev_id
                
        if best_id is not None:
            current_wrists[best_id] = (wx, wy)
            velocities[best_id] = min_dist
        else:
            new_id = i
            while new_id in current_wrists or new_id in prev_wrists:
                new_id += 1
            current_wrists[new_id] = (wx, wy)
            velocities[new_id] = 0.0
            
    return current_wrists, velocities

def draw_semi_transparent_rect(img, pt1, pt2, color, alpha):
    x1, y1 = max(0, pt1[0]), max(0, pt1[1])
    x2, y2 = min(img.shape[1], pt2[0]), min(img.shape[0], pt2[1])
    if x2 <= x1 or y2 <= y1:
        return
    sub_img = img[y1:y2, x1:x2]
    rect = np.zeros_like(sub_img)
    rect[:] = color
    blend = cv2.addWeighted(sub_img, 1.0 - alpha, rect, alpha, 0)
    img[y1:y2, x1:x2] = blend

def main():
    camera_index = choose_camera()
    cap = cv2.VideoCapture(camera_index)
    
    # Start at 640x360 for high performance out of the box
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

    # Let camera adjust and grab initial frame dimensions
    for _ in range(5):
        success, image = cap.read()
    
    h, w, _ = image.shape
    state = AppState(w, h)

    # Set up MediaPipe options with VIDEO mode for temporal tracking
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=2,
        min_hand_detection_confidence=0.55,
        min_hand_presence_confidence=0.55,
        min_tracking_confidence=0.6,
        running_mode=vision.RunningMode.VIDEO
    )

    with vision.HandLandmarker.create_from_options(options) as landmarker:
        print("Starting camera... Controls:")
        print("  0-8 : Switch visual effects")
        print("  R   : Toggle resolution (720p / 360p)")
        print("  B   : Toggle Glow Mode (Optimized / Standard / Off)")
        print("  D   : Toggle Diagnostic HUD")
        print("  Q   : Quit")
        
        # Pre-allocate reuseable canvas buffer
        canvas = np.zeros((h, w, 3), dtype=np.uint8)
        
        fps_prev_time = time.time()
        fps_frame_count = 0
        current_fps = 0.0
        
        while cap.isOpened():
            loop_start = time.perf_counter()
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                break

            image = cv2.flip(image, 1)
            frame_h, frame_w, _ = image.shape
            
            # Re-initialize state sizes dynamically if camera resolution changes
            if frame_w != state.w or frame_h != state.h:
                state.init_ripple_maps(frame_w, frame_h)
                canvas = np.zeros((frame_h, frame_w, 3), dtype=np.uint8)
                state.ghost_buffer.clear()
                state.particles.clear()
                state.orbit_particles.clear()
                state.digital_chars.clear()
            
            # Reuse canvas by clearing it in-place
            canvas.fill(0)
            
            # Darkened background for neon glow
            background = cv2.convertScaleAbs(image, alpha=0.3, beta=0)
            
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
            
            # Inference using current timestamp
            timestamp_ms = int(time.time() * 1000)
            inference_start = time.perf_counter()
            results = landmarker.detect_for_video(mp_image, timestamp_ms)
            inference_time = (time.perf_counter() - inference_start) * 1000
            
            # Hand tracking and velocity calculations
            num_detected = len(results.hand_landmarks) if results.hand_landmarks else 0
            if results.hand_landmarks:
                state.prev_wrists, state.hand_velocities = track_hands(
                    results.hand_landmarks, state.prev_wrists, state.w, state.h
                )
            else:
                state.prev_wrists.clear()
                state.hand_velocities.clear()
                
            # Cycle colors based on distance or absolute time
            color = (130, 255, 120)  # default bright green
            hands_distance = 0.0
            
            if num_detected == 2:
                hand1 = results.hand_landmarks[0]
                hand2 = results.hand_landmarks[1]
                h1_wrist = (int(hand1[0].x * state.w), int(hand1[0].y * state.h))
                h2_wrist = (int(hand2[0].x * state.w), int(hand2[0].y * state.h))
                hands_distance = math.hypot(h1_wrist[0] - h2_wrist[0], h1_wrist[1] - h2_wrist[1])
                color = get_dynamic_color(hands_distance, max_distance=state.w * 0.7)
            elif num_detected == 1:
                color = get_dynamic_color(200, max_distance=state.w)
                
            # Effect rendering phase
            effect_render_start = time.perf_counter()
            
            # --- EFFECT 1: Inversion Portal (Negative Box) ---
            if state.active_effect == 1 and results.hand_landmarks:
                # Limit thickness bounds [1, 3] to avoid OpenCV assertions
                pulse_thickness = max(1, int(2 + math.sin(time.time() * 10) * 1.2))
                for hand in results.hand_landmarks:
                    # Bounding box of landmarks
                    xs = [lm.x * state.w for lm in hand]
                    ys = [lm.y * state.h for lm in hand]
                    xmin, xmax = int(min(xs)) - 30, int(max(xs)) + 30
                    ymin, ymax = int(min(ys)) - 30, int(max(ys)) + 30
                    
                    xmin, xmax = max(0, xmin), min(state.w, xmax)
                    ymin, ymax = max(0, ymin), min(state.h, ymax)
                    
                    if xmax > xmin and ymax > ymin:
                        # Invert frame colors in the box area
                        image[ymin:ymax, xmin:xmax] = cv2.bitwise_not(image[ymin:ymax, xmin:xmax])
                        # Draw high-tech HUD corners around portal box
                        draw_hud_corners(canvas, (xmin, ymin), (xmax, ymax), color, thickness=pulse_thickness, length=20)

            # --- EFFECT 2: Energy Pulse (Lightning) ---
            elif state.active_effect == 2 and results.hand_landmarks:
                # Radial discharges from all visible hands' fingertips (NO lines between the hands)
                for hand_idx, hand in enumerate(results.hand_landmarks):
                    # Try to fetch current hand velocity
                    vel = 0.0
                    wx = int(hand[0].x * state.w)
                    wy = int(hand[0].y * state.h)
                    for prev_id, prev_loc in state.prev_wrists.items():
                        dist = math.hypot(wx - prev_loc[0], wy - prev_loc[1])
                        if dist < 180:
                            vel = dist
                            break
                    
                    # Number of discharges and displacement bounds scale with speed
                    sparks_count = int(2 + min(vel * 0.2, 5))
                    disp = int(6 + min(vel * 0.6, 20))
                    
                    for tip_idx in FINGER_TIPS:
                        tx = int(hand[tip_idx].x * state.w)
                        ty = int(hand[tip_idx].y * state.h)
                        
                        for s in range(sparks_count):
                            angle = np.random.uniform(0, 2 * math.pi)
                            length = int(18 + vel * np.random.uniform(0.8, 2.4))
                            end_x = int(tx + math.cos(angle) * length)
                            end_y = int(ty + math.sin(angle) * length)
                            
                            # Draw dual-stroke glowing arc radiating out
                            draw_lightning(canvas, (tx, ty), (end_x, end_y), color=color, thickness=2, displace=disp)
                            draw_lightning(canvas, (tx, ty), (end_x, end_y), color=(255, 255, 255), thickness=1, displace=disp)

            # --- EFFECT 3: Motion Ghost Trail ---
            elif state.active_effect == 3:
                # Update ghost history trail
                if results.hand_landmarks:
                    current_lms = []
                    for hand in results.hand_landmarks:
                        current_lms.append([(int(lm.x * state.w), int(lm.y * state.h)) for lm in hand])
                    state.ghost_buffer.append(current_lms)
                else:
                    state.ghost_buffer.append([])
                    
                state.ghost_buffer = state.ghost_buffer[-7:] # maintain history size
                
                # Render previous poses with fading alpha and gradient shift (Skeletal only, no inter-hand links)
                ghost_canvas = np.zeros_like(canvas)
                for age, frame_hands in enumerate(state.ghost_buffer[:-1]):
                    alpha = (age + 1) / len(state.ghost_buffer) * 0.5
                    ghost_color = (240, 100, 70) if age % 2 == 0 else (170, 70, 240)
                    
                    for hand in frame_hands:
                        for pt in hand:
                            cv2.circle(ghost_canvas, pt, 4, ghost_color, -1)
                        # Connect ghost skeletal bones
                        for start_idx, end_idx in HAND_CONNECTIONS:
                            pt1 = hand[start_idx]
                            pt2 = hand[end_idx]
                            cv2.line(ghost_canvas, pt1, pt2, ghost_color, 2, cv2.LINE_AA)
                            
                canvas = cv2.addWeighted(canvas, 1.0, ghost_canvas, 1.0, 0)

            # --- EFFECT 4: Particle Shower ---
            elif state.active_effect == 4:
                # Spawn sparkles from fingers
                if results.hand_landmarks:
                    for hand_id, vel in state.hand_velocities.items():
                        hand_idx = min(hand_id, num_detected - 1)
                        if hand_idx >= 0:
                            hand = results.hand_landmarks[hand_idx]
                            for tip_idx in FINGER_TIPS:
                                tx = int(hand[tip_idx].x * state.w)
                                ty = int(hand[tip_idx].y * state.h)
                                
                                # Spark counts scale with hand velocity
                                spawn_n = int(1 + min(vel * 0.25, 4))
                                for _ in range(spawn_n):
                                    vx = np.random.uniform(-4.5, 4.5)
                                    vy = np.random.uniform(-7.0, -2.0)
                                    life = np.random.uniform(0.3, 0.7)
                                    state.particles.append([tx, ty, vx, vy, life, color])
                                    
                # Update, draw, and decay active particles
                new_particles = []
                for p in state.particles:
                    px, py, p_vx, p_vy, p_life, p_color = p
                    px += p_vx
                    py += p_vy
                    p_vy += 0.35  # gravity pull
                    p_life -= 0.033 # simulated delta time
                    
                    if p_life > 0 and 0 <= px < state.w and 0 <= py < state.h:
                        r = int(p_life * 7) + 1
                        cv2.circle(canvas, (int(px), int(py)), r, p_color, -1)
                        new_particles.append([px, py, p_vx, p_vy, p_life, p_color])
                        
                state.particles = new_particles[-180:] # bound particle counts for CPU safety

            # --- EFFECT 5: Ripple Distortion (Liquid Image Warp) ---
            elif state.active_effect == 5 and results.hand_landmarks:
                curr_map_x = state.map_x.copy()
                curr_map_y = state.map_y.copy()
                
                # Apply distortion mapping centered at hand centers
                for hand_id, vel in state.hand_velocities.items():
                    hand_idx = min(hand_id, num_detected - 1)
                    if hand_idx >= 0:
                        hand = results.hand_landmarks[hand_idx]
                        cx = int(hand[9].x * state.w) # Middle finger MCP joint center
                        cy = int(hand[9].y * state.h)
                        
                        # Shockwave ripple size and speed based on velocity
                        amp = int(4.0 + min(vel * 1.5, 32.0))
                        radius = int(state.w * 0.22)
                        
                        x_min = max(0, cx - radius)
                        x_max = min(state.w, cx + radius)
                        y_min = max(0, cy - radius)
                        y_max = min(state.h, cy + radius)
                        
                        if x_max > x_min and y_max > y_min:
                            lx = state.map_x[y_min:y_max, x_min:x_max] - cx
                            ly = state.map_y[y_min:y_max, x_min:x_max] - cy
                            r = np.sqrt(lx**2 + ly**2)
                            r_safe = np.where(r == 0, 1.0, r)
                            
                            pulse = time.time() * 8.5
                            displacement = amp * np.sin(r / 10.0 - pulse) * np.exp(-r / (radius * 0.6))
                            
                            dx = (lx / r_safe) * displacement
                            dy = (ly / r_safe) * displacement
                            
                            curr_map_x[y_min:y_max, x_min:x_max] += dx.astype(np.float32)
                            curr_map_y[y_min:y_max, x_min:x_max] += dy.astype(np.float32)
                            
                image = cv2.remap(image, curr_map_x, curr_map_y, cv2.INTER_LINEAR)
                # Re-apply scale adjust to background as image just got warped
                background = cv2.convertScaleAbs(image, alpha=0.3, beta=0)

            # --- EFFECT 6: Thermal Vision ---
            elif state.active_effect == 6 and results.hand_landmarks:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                thermal = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
                
                # Performance optimized: generate proximity heat mask at 4x lower scale
                sw, sh = state.w // 4, state.h // 4
                small_mask = np.zeros((sh, sw), dtype=np.uint8)
                for hand in results.hand_landmarks:
                    for lm in hand:
                        lx = int(lm.x * sw)
                        ly = int(lm.y * sh)
                        cv2.circle(small_mask, (lx, ly), 9, 255, -1)
                        
                # Fast downsized blur and scale back up
                small_mask_blurred = cv2.GaussianBlur(small_mask, (13, 13), 0)
                mask = cv2.resize(small_mask_blurred, (state.w, state.h), interpolation=cv2.INTER_LINEAR)
                mask_f = mask.astype(np.float32) / 255.0
                
                # Cool-tinted dark background scene
                bg_cool = cv2.convertScaleAbs(image, alpha=0.4, beta=0)
                bg_cool[:, :, 0] = cv2.add(bg_cool[:, :, 0], 25) # Blue channel additive tint
                
                # Blend heat and cool fields
                mask_f_expanded = mask_f[:, :, np.newaxis]
                image = (bg_cool * (1.0 - mask_f_expanded) + thermal * mask_f_expanded).astype(np.uint8)
                background = cv2.convertScaleAbs(image, alpha=0.3, beta=0)

            # --- NEW EFFECT 7: Particle Orbit (Gravity Well) ---
            elif state.active_effect == 7 and results.hand_landmarks:
                # Draw central gravitational pulse at hand centers
                for hand_idx, hand in enumerate(results.hand_landmarks):
                    cx = int(hand[9].x * state.w)
                    cy = int(hand[9].y * state.h)
                    
                    # Fetch velocity of the hand
                    vel = 0.0
                    for prev_id, prev_loc in state.prev_wrists.items():
                        dist = math.hypot(cx - prev_loc[0], cy - prev_loc[1])
                        if dist < 180:
                            vel = dist
                            break
                            
                    # Pulse glowing circles at the hand center
                    pulse_r = int(12 + math.sin(time.time() * 12) * 5)
                    cv2.circle(canvas, (cx, cy), pulse_r, color, 1, cv2.LINE_AA)
                    cv2.circle(canvas, (cx, cy), pulse_r + 6, color, 2, cv2.LINE_AA)
                    
                    # Spawn orbiting particles around this center
                    if len(state.orbit_particles) < 120:
                        for _ in range(3):
                            angle = np.random.uniform(0, 2 * math.pi)
                            radius = np.random.uniform(25, 90)
                            # Orbit speed scales up with hand speed
                            speed = np.random.uniform(0.04, 0.12) + (vel * 0.003)
                            # Randomize direction
                            if np.random.rand() > 0.5:
                                speed = -speed
                            life = np.random.uniform(0.5, 1.0)
                            color_offset = np.random.randint(-20, 20)
                            state.orbit_particles.append([cx, cy, angle, radius, speed, life, color_offset])
                
                # Update and render orbiting particles
                new_orbit_parts = []
                for op in state.orbit_particles:
                    cx, cy, o_angle, o_radius, o_speed, o_life, o_offset = op
                    # Orbit rotation
                    o_angle += o_speed
                    o_life -= 0.02
                    
                    # Slowly spiral closer/further
                    o_radius += math.sin(time.time() * 3) * 0.5
                    
                    px = int(cx + math.cos(o_angle) * o_radius)
                    py = int(cy + math.sin(o_angle) * o_radius)
                    
                    if o_life > 0 and 0 <= px < state.w and 0 <= py < state.h:
                        # Slight HSV color shift
                        p_color = (max(0, min(255, color[0] + o_offset)),
                                   max(0, min(255, color[1] + o_offset)),
                                   max(0, min(255, color[2] + o_offset)))
                        
                        r = int(o_life * 5) + 1
                        cv2.circle(canvas, (px, py), r, p_color, -1)
                        # Orbit trail
                        cv2.circle(canvas, (px, py), r + 2, (255, 255, 255), 1, cv2.LINE_AA)
                        
                        new_orbit_parts.append([cx, cy, o_angle, o_radius, o_speed, o_life, o_offset])
                state.orbit_particles = new_orbit_parts[-150:]

            # --- NEW EFFECT 8: Digital Rain Aura (Matrix Proximity) ---
            elif state.active_effect == 8 and results.hand_landmarks:
                # Generate green digital character structures radiating from hand landmarks
                for hand in results.hand_landmarks:
                    # Spawn characters at random joints
                    if np.random.rand() > 0.25:
                        joint_idx = np.random.randint(0, 21)
                        jx = int(hand[joint_idx].x * state.w)
                        jy = int(hand[joint_idx].y * state.h)
                        
                        # Generate random alphanumeric or binary character
                        char = random.choice("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ#@$%&*")
                        speed = np.random.uniform(1.5, 4.0)
                        life = np.random.uniform(0.6, 1.2)
                        
                        # Light green matrices with random green/cyan hues
                        g_color = (np.random.randint(50, 100), np.random.randint(200, 255), np.random.randint(50, 150))
                        state.digital_chars.append([jx, jy, char, speed, life, g_color])
                
                # Update, slide up, and draw the characters
                new_chars = []
                for dc in state.digital_chars:
                    dx, dy, d_char, d_speed, d_life, d_color = dc
                    dy -= d_speed  # Floating upwards
                    d_life -= 0.03
                    
                    if d_life > 0 and dy > 0:
                        # Character scale decays with life
                        scale = d_life * 0.45
                        # Render characters on canvas
                        cv2.putText(canvas, d_char, (int(dx), int(dy)), 
                                    cv2.FONT_HERSHEY_SIMPLEX, scale, d_color, 1, cv2.LINE_AA)
                        new_chars.append([dx, dy, d_char, d_speed, d_life, d_color])
                state.digital_chars = new_chars[-120:]

            # --- RENDER HAND JOINT OVERLAYS ---
            # Render internal skeleton within each hand independently (No lines between the hands)
            if state.active_effect != 6: # Skip joint overlays in thermal view to keep look clean
                if results.hand_landmarks:
                    for hand in results.hand_landmarks:
                        # Draw skeletal connecting bones internally
                        for start_idx, end_idx in HAND_CONNECTIONS:
                            pt1 = (int(hand[start_idx].x * state.w), int(hand[start_idx].y * state.h))
                            pt2 = (int(hand[end_idx].x * state.w), int(hand[end_idx].y * state.h))
                            cv2.line(canvas, pt1, pt2, color=(255, 255, 255), thickness=1, lineType=cv2.LINE_AA)
                            cv2.line(canvas, pt1, pt2, color=color, thickness=2, lineType=cv2.LINE_AA)
                        
                        # Draw joint nodes
                        for landmark in hand:
                            x, y = int(landmark.x * state.w), int(landmark.y * state.h)
                            cv2.circle(canvas, (x, y), 2, (255, 255, 255), -1)
                            cv2.circle(canvas, (x, y), 5, color, 1, cv2.LINE_AA)
            
            # --- RENDER GLOW & MERGE IMAGES ---
            glow_start = time.perf_counter()
            if state.glow_mode == 0:
                # Downscaled blur: Resize 4x down, blur, scale up (70% CPU cycles saved)
                small_canvas = cv2.resize(canvas, (state.w // 4, state.h // 4), interpolation=cv2.INTER_LINEAR)
                glow_small = cv2.GaussianBlur(small_canvas, (5, 5), 0)
                glow = cv2.resize(glow_small, (state.w, state.h), interpolation=cv2.INTER_LINEAR)
                canvas_glow = cv2.addWeighted(canvas, 0.8, glow, 1.2, 0)
                final_image = cv2.addWeighted(background, 1.0, canvas_glow, 1.0, 0)
            elif state.glow_mode == 1:
                # Heavy direct blur
                glow = cv2.GaussianBlur(canvas, (19, 19), 0)
                canvas_glow = cv2.addWeighted(canvas, 0.8, glow, 1.2, 0)
                final_image = cv2.addWeighted(background, 1.0, canvas_glow, 1.0, 0)
            else:
                # Glow off
                final_image = cv2.addWeighted(background, 1.0, canvas, 1.0, 0)
                
            glow_time = (time.perf_counter() - glow_start) * 1000
            effect_time = (time.perf_counter() - effect_render_start) * 1000

            # --- DIAGNOSTIC HUD OVERLAY ---
            if state.show_hud:
                # HUD background panel (Extended height slightly for 9 modes)
                draw_semi_transparent_rect(final_image, (10, 10), (320, 160), (18, 18, 22), 0.75)
                cv2.rectangle(final_image, (10, 10), (320, 160), (80, 80, 95), 1, cv2.LINE_AA)
                
                # Active effect text
                effect_name = EFFECT_NAMES.get(state.active_effect, "None")
                cv2.putText(final_image, f"Mode: {effect_name}", (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (99, 102, 241), 1, cv2.LINE_AA)
                
                # Performance parameters
                cv2.putText(final_image, f"FPS: {current_fps:.1f} Hz", (20, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (230, 230, 240), 1, cv2.LINE_AA)
                cv2.putText(final_image, f"Inference: {inference_time:.1f} ms", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 210), 1, cv2.LINE_AA)
                cv2.putText(final_image, f"Effect/Blur: {effect_time:.1f} / {glow_time:.1f} ms", (20, 88), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 210), 1, cv2.LINE_AA)
                
                # Configuration statuses
                glow_status = "Downsampled Blur" if state.glow_mode == 0 else ("Direct Blur" if state.glow_mode == 1 else "Glow Disabled")
                cv2.putText(final_image, f"Glow: {glow_status}", (20, 108), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (170, 230, 180), 1, cv2.LINE_AA)
                cv2.putText(final_image, f"Resolution: {state.w}x{state.h}", (20, 126), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 220, 240), 1, cv2.LINE_AA)
                cv2.putText(final_image, f"Delegate: CPU (TFLite XNNPACK)", (20, 144), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (240, 200, 150), 1, cv2.LINE_AA)
                
                # Bottom info instruction text bar (Updated control hints)
                draw_semi_transparent_rect(final_image, (0, final_image.shape[0] - 25), (final_image.shape[1], final_image.shape[0]), (10, 10, 12), 0.85)
                cv2.putText(final_image, "Controls: [0-8] Effects | [R] Res | [B] Glow Mode | [D] HUD | [Q] Exit", 
                            (12, final_image.shape[0] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 210), 1, cv2.LINE_AA)

            cv2.imshow('MediaPipe Hand Tricks - Press Q to Exit', final_image)
            
            # --- KEYBOARD CONTROLS PROCESSING ---
            key = cv2.waitKey(5) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('d'):
                state.show_hud = not state.show_hud
            elif key == ord('b'):
                state.glow_mode = (state.glow_mode + 1) % 3
            elif key == ord('r'):
                # Toggle Resolution: 720p <-> 360p
                new_w, new_h = (1280, 720) if state.w == 640 else (640, 360)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, new_w)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, new_h)
                # Flush camera queue buffer
                for _ in range(3):
                    cap.read()
            elif ord('0') <= key <= ord('8'):
                state.active_effect = key - ord('0')

            # Calculate FPS smoothly over intervals
            fps_frame_count += 1
            elapsed = time.time() - fps_prev_time
            if elapsed >= 0.5:
                current_fps = fps_frame_count / elapsed
                fps_frame_count = 0
                fps_prev_time = time.time()
                
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
