import sys

missing_packages = []
try:
    import cv2
except ModuleNotFoundError:
    cv2 = None
    missing_packages.append('opencv-python')

try:
    import mediapipe as mp
except ModuleNotFoundError:
    mp = None
    missing_packages.append('mediapipe')

try:
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
except Exception:
    python = None
    vision = None
    if mp is None:
        pass
    else:
        print('Error importing MediaPipe tasks. Ensure MediaPipe is installed and compatible with your Python version.')
        sys.exit(1)

try:
    import numpy as np
except ModuleNotFoundError:
    np = None
    missing_packages.append('numpy')

import math
import time
import tkinter as tk
from tkinter import ttk
import threading
import random
import os

try:
    import winsound
except ModuleNotFoundError:
    winsound = None

# Optional WebSocket broadcaster for remote 3D control
try:
    import ws_server
except Exception:
    ws_server = None

if missing_packages:
    print('Missing required Python package(s):', ', '.join(missing_packages))
    print('Install them using: pip install -r requirements.txt')
    print('If using a virtual environment, activate it first and make sure the correct interpreter is selected.')
    sys.exit(1)

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

# Palm-related landmark indices used to suppress palm lines when cube/zoom active
PALM_INDICES = {0, 1, 5, 9, 13, 17}

EFFECT_NAMES = {
    0: "Standard Glow",
    1: "Inversion Portal",
    2: "Energy Pulse",
    3: "Motion Ghost Trail",
    4: "Particle Shower",
    5: "Ripple Distortion",
    6: "Thermal Vision",
    7: "Particle Orbit",
    8: "Digital Rain Aura",
    9: "Goku Power Core"
}

def choose_camera():
    selected_camera = [0]
    
    root = tk.Tk()
    root.title("Antigravity - Select Camera")
    root.geometry("380x350")
    root.configure(bg="#121214")
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
        
        disp = np.random.uniform(-displace, displace)
        px += nx * disp
        py += ny * disp
        
        points.append((int(px), int(py)))
        
    points.append(pt2)
    
    for i in range(len(points) - 1):
        cv2.line(img, points[i], points[i+1], color, thickness, cv2.LINE_AA)

class AppState:
    def __init__(self, w, h):
        self.active_effect = 0  # 0 to 9
        self.show_hud = True
        self.w = w
        self.h = h
        self.glow_mode = 0  # 0: Optimized, 1: Standard, 2: Off
        self.fullscreen = False
        # New feature flags
        self.hide_hand_lines = False  # If True, don't draw skeletal lines/outline
        self.enable_cube = False      # Toggle faux 3D cube overlay
        self.zoom_enabled = True      # Whether pinch zoom is active
        self.zoom_factor = 1.0        # Current smooth zoom factor (1.0 = normal)
        self.grabbed = False          # Whether object is grabbed by pinch
        self.cube = {
            'pos': (w//2, h//2),
            'size': max(40, min(w, h) // 6),
            'angle': 0.0,
            'base_size': max(40, min(w, h) // 6),
            'vel': {'x': 0.0, 'y': 0.0, 'rot_x': 0.0, 'rot_y': 0.0},
            'damping': 0.90,
            'snap_threshold': max(24, min(w, h) // 12),
            'snap_speed': 0.18
        }
        self.prev_index_pos = None
        # Rotation angles (degrees) and scale multiplier
        self.cube['rot_x'] = 0.0
        self.cube['rot_y'] = 0.0
        self.cube['scale'] = 1.0
        self.ws_running = False
        self.ws_port = 8765
        
        # Velocity Tracking
        self.prev_wrists = {}  # {hand_idx: (x, y)}
        self.hand_velocities = {}  # {hand_idx: float}
        
        # Ghost Trail
        self.ghost_buffer = []
        
        # Particle System
        self.particles = []
        
        # Particle Orbit System
        self.orbit_particles = []
        
        # Digital Rain Aura Characters
        self.digital_chars = []
        
        # Goku Power Aura System
        self.goku_particles = []
        self.goku_sound_cooldown = 0
        
        # Capture & Record Flags
        self.trigger_capture = False
        self.trigger_record = False
        self.is_recording = False
        self.video_writer = None
        self.notification_text = ""
        self.notification_time = 0.0
        
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

    def set_notification(self, text):
        self.notification_text = text
        self.notification_time = time.time() + 2.0

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

def draw_cube(canvas, center, size, angle_deg, color=(200,180,255)):
    # Simple faux 3D cube drawn using projected offsets
    cx, cy = center
    s = int(size)
    a = math.radians(angle_deg)
    rx = math.radians(int(getattr(canvas, '_rot_x', 0))) if hasattr(canvas, '_rot_x') else 0
    ry = math.radians(int(getattr(canvas, '_rot_y', 0))) if hasattr(canvas, '_rot_y') else 0
    # base square
    half = s // 2
    p1 = (cx - half, cy - half)
    p2 = (cx + half, cy - half)
    p3 = (cx + half, cy + half)
    p4 = (cx - half, cy + half)

    # offset for top face (simulate 3D) influenced by rotation x/y
    ox = int(math.cos(a + ry) * half * 0.6)
    oy = int(-math.sin(a + rx) * half * 0.45) - int(half * 0.25)

    q1 = (p1[0] + ox, p1[1] + oy)
    q2 = (p2[0] + ox, p2[1] + oy)
    q3 = (p3[0] + ox, p3[1] + oy)
    q4 = (p4[0] + ox, p4[1] + oy)

    # draw faces: edges with gradient
    faces = [ (p1,p2,p3,p4), (q1,q2,q3,q4) ]
    # Draw base and top
    # draw a soft shadow under the cube for depth
    try:
        shadow = canvas.copy()
        sx = int(size * 0.9)
        sy = int(size * 0.45)
        cv2.ellipse(shadow, (cx, cy + int(size*0.6)), (sx, sy), 0, 0, 360, (10,10,10), -1)
        cv2.GaussianBlur(shadow, (21,21), 0, dst=shadow)
        cv2.addWeighted(shadow, 0.18, canvas, 0.82, 0, canvas)
    except Exception:
        pass

    # face fill with gradient-like shading
    try:
        overlay = canvas.copy()
        # darker base face
        cv2.fillPoly(overlay, [np.array(faces[0], np.int32)], (int(color[0]*0.45), int(color[1]*0.45), int(color[2]*0.45)))
        # lighter top face
        cv2.fillPoly(overlay, [np.array(faces[1], np.int32)], (min(255,int(color[0]*0.9)), min(255,int(color[1]*0.9)), min(255,int(color[2]*0.9))))
        cv2.addWeighted(overlay, 0.28, canvas, 0.72, 0, canvas)
    except Exception:
        pass

    # outline edges with soft highlights
    cv2.polylines(canvas, [np.array(faces[0], np.int32)], True, (40,40,45), 2, cv2.LINE_AA)
    cv2.polylines(canvas, [np.array(faces[1], np.int32)], True, (210,210,230), 2, cv2.LINE_AA)
    # Connect edges
    for pa, qa in zip(faces[0], faces[1]):
        cv2.line(canvas, pa, qa, (140,130,180), 2, cv2.LINE_AA)

def _set_canvas_rotation(canvas, rot_x, rot_y):
    # attach small attributes so draw_cube can read them
    try:
        setattr(canvas, '_rot_x', int(rot_x))
        setattr(canvas, '_rot_y', int(rot_y))
    except Exception:
        pass

def pinch_distance(hand):
    # Compute distance between thumb tip (4) and index tip (8) if available
    if not hand:
        return None
    if len(hand) <= 8:
        return None
    x1, y1 = hand[4].x, hand[4].y
    x2, y2 = hand[8].x, hand[8].y
    return math.hypot(x1 - x2, y1 - y2)

# Sound Synthesizer Functions (native, background-threaded)
def play_beep_async(freq, duration):
    def play():
        try:
            winsound.Beep(freq, duration)
        except:
            pass
    threading.Thread(target=play, daemon=True).start()

def play_shutter_sound():
    play_beep_async(1800, 60)

def play_rec_start():
    def play():
        try:
            winsound.Beep(880, 80)
            winsound.Beep(1100, 80)
        except:
            pass
    threading.Thread(target=play, daemon=True).start()

def play_rec_stop():
    def play():
        try:
            winsound.Beep(1100, 80)
            winsound.Beep(880, 80)
        except:
            pass
    threading.Thread(target=play, daemon=True).start()

def play_kamehameha_charge():
    def play():
        try:
            # Synth power sweep up
            for f in range(120, 520, 15):
                winsound.Beep(f, 15)
            # Energy charge pulse
            for _ in range(3):
                winsound.Beep(random.randint(550, 750), 30)
        except:
            pass
    threading.Thread(target=play, daemon=True).start()

# Click callbacks for UI buttons
def mouse_callback(event, x, y, flags, param):
    state = param
    if event == cv2.EVENT_LBUTTONDOWN:
        # Camera / Photo Button: [w - 110, 15] to [w - 65, 45]
        if state.w - 110 <= x <= state.w - 65 and 15 <= y <= 45:
            state.trigger_capture = True
        # Recording / Video Button: [w - 55, 15] to [w - 10, 45]
        elif state.w - 55 <= x <= state.w - 10 and 15 <= y <= 45:
            state.trigger_record = True

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

    # Create folder for saving captures if it doesn't exist
    if not os.path.exists('captures'):
        os.makedirs('captures')

    # Setup namedWindow as NORMAL to support dynamic resizing and fullscreen fills
    window_name = 'MediaPipe Hand Tricks - Press Q to Exit'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, mouse_callback, state)

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
        print("  0-9 : Switch visual effects")
        print("  R   : Toggle resolution (720p / 360p)")
        print("  B   : Toggle Glow Mode (Optimized / Standard / Off)")
        print("  D   : Toggle Diagnostic HUD")
        print("  F   : Toggle Fullscreen Window")
        print("  C   : Capture Image screenshot")
        print("  V   : Toggle Video Recording")
        print("  Q   : Quit")
        
        # Pre-allocate canvas buffer
        canvas = np.zeros((h, w, 3), dtype=np.uint8)
        
        fps_prev_time = time.time()
        fps_frame_count = 0
        current_fps = 0.0
        
        while cap.isOpened():
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
                state.goku_particles.clear()
                # If resolution changed while recording, force stop the recording
                if state.is_recording:
                    state.is_recording = False
                    if state.video_writer:
                        state.video_writer.release()
                        state.video_writer = None
                    state.set_notification("Record Stopped (Resolution Changed)")
                    play_rec_stop()
            
            # Clear canvas buffer
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
            # Publish landmarks to WebSocket broadcaster (if running)
            try:
                if ws_server is not None and state.ws_running:
                    hands_data = []
                    if results.hand_landmarks:
                        for hand in results.hand_landmarks:
                            hand_list = []
                            for lm in hand:
                                hand_list.append({'x': float(lm.x), 'y': float(lm.y), 'z': float(getattr(lm, 'z', 0.0))})
                            hands_data.append(hand_list)
                    ws_server.latest_landmarks = hands_data
            except Exception:
                pass
            
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
            color = (130, 255, 120)  # default green
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
                pulse_thickness = max(1, int(2 + math.sin(time.time() * 10) * 1.2))
                for hand in results.hand_landmarks:
                    xs = [lm.x * state.w for lm in hand]
                    ys = [lm.y * state.h for lm in hand]
                    xmin, xmax = int(min(xs)) - 30, int(max(xs)) + 30
                    ymin, ymax = int(min(ys)) - 30, int(max(ys)) + 30
                    
                    xmin, xmax = max(0, xmin), min(state.w, xmax)
                    ymin, ymax = max(0, ymin), min(state.h, ymax)
                    
                    if xmax > xmin and ymax > ymin:
                        image[ymin:ymax, xmin:xmax] = cv2.bitwise_not(image[ymin:ymax, xmin:xmax])
                        draw_hud_corners(canvas, (xmin, ymin), (xmax, ymax), color, thickness=pulse_thickness, length=20)

            # --- EFFECT 2: Energy Pulse (Lightning) ---
            elif state.active_effect == 2 and results.hand_landmarks:
                for hand_idx, hand in enumerate(results.hand_landmarks):
                    vel = 0.0
                    wx = int(hand[0].x * state.w)
                    wy = int(hand[0].y * state.h)
                    for prev_id, prev_loc in state.prev_wrists.items():
                        dist = math.hypot(wx - prev_loc[0], wy - prev_loc[1])
                        if dist < 180:
                            vel = dist
                            break
                    
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
                            
                            draw_lightning(canvas, (tx, ty), (end_x, end_y), color=color, thickness=2, displace=disp)
                            draw_lightning(canvas, (tx, ty), (end_x, end_y), color=(255, 255, 255), thickness=1, displace=disp)

            # --- EFFECT 3: Motion Ghost Trail ---
            elif state.active_effect == 3:
                if results.hand_landmarks:
                    current_lms = []
                    for hand in results.hand_landmarks:
                        current_lms.append([(int(lm.x * state.w), int(lm.y * state.h)) for lm in hand])
                    state.ghost_buffer.append(current_lms)
                else:
                    state.ghost_buffer.append([])
                    
                state.ghost_buffer = state.ghost_buffer[-7:]
                
                ghost_canvas = np.zeros_like(canvas)
                for age, frame_hands in enumerate(state.ghost_buffer[:-1]):
                    alpha = (age + 1) / len(state.ghost_buffer) * 0.5
                    ghost_color = (240, 100, 70) if age % 2 == 0 else (170, 70, 240)
                    
                    for hand in frame_hands:
                        for pt in hand:
                            cv2.circle(ghost_canvas, pt, 4, ghost_color, -1)
                        for start_idx, end_idx in HAND_CONNECTIONS:
                            pt1 = hand[start_idx]
                            pt2 = hand[end_idx]
                            cv2.line(ghost_canvas, pt1, pt2, ghost_color, 2, cv2.LINE_AA)
                            
                canvas = cv2.addWeighted(canvas, 1.0, ghost_canvas, 1.0, 0)

            # --- EFFECT 4: Particle Shower ---
            elif state.active_effect == 4:
                if results.hand_landmarks:
                    for hand_id, vel in state.hand_velocities.items():
                        hand_idx = min(hand_id, num_detected - 1)
                        if hand_idx >= 0:
                            hand = results.hand_landmarks[hand_idx]
                            for tip_idx in FINGER_TIPS:
                                tx = int(hand[tip_idx].x * state.w)
                                ty = int(hand[tip_idx].y * state.h)
                                
                                spawn_n = int(1 + min(vel * 0.25, 4))
                                for _ in range(spawn_n):
                                    vx = np.random.uniform(-4.5, 4.5)
                                    vy = np.random.uniform(-7.0, -2.0)
                                    life = np.random.uniform(0.3, 0.7)
                                    state.particles.append([tx, ty, vx, vy, life, color])
                                    
                new_particles = []
                for p in state.particles:
                    px, py, p_vx, p_vy, p_life, p_color = p
                    px += p_vx
                    py += p_vy
                    p_vy += 0.35
                    p_life -= 0.033
                    
                    if p_life > 0 and 0 <= px < state.w and 0 <= py < state.h:
                        r = int(p_life * 7) + 1
                        cv2.circle(canvas, (int(px), int(py)), r, p_color, -1)
                        new_particles.append([px, py, p_vx, p_vy, p_life, p_color])
                state.particles = new_particles[-180:]

            # --- EFFECT 5: Ripple Distortion ---
            elif state.active_effect == 5 and results.hand_landmarks:
                curr_map_x = state.map_x.copy()
                curr_map_y = state.map_y.copy()
                
                for hand_id, vel in state.hand_velocities.items():
                    hand_idx = min(hand_id, num_detected - 1)
                    if hand_idx >= 0:
                        hand = results.hand_landmarks[hand_idx]
                        cx = int(hand[9].x * state.w)
                        cy = int(hand[9].y * state.h)
                        
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
                background = cv2.convertScaleAbs(image, alpha=0.3, beta=0)

            # --- EFFECT 6: Thermal Vision ---
            elif state.active_effect == 6 and results.hand_landmarks:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                thermal = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
                
                sw, sh = state.w // 4, state.h // 4
                small_mask = np.zeros((sh, sw), dtype=np.uint8)
                for hand in results.hand_landmarks:
                    for lm in hand:
                        lx = int(lm.x * sw)
                        ly = int(lm.y * sh)
                        cv2.circle(small_mask, (lx, ly), 9, 255, -1)
                        
                small_mask_blurred = cv2.GaussianBlur(small_mask, (13, 13), 0)
                mask = cv2.resize(small_mask_blurred, (state.w, state.h), interpolation=cv2.INTER_LINEAR)
                mask_f = mask.astype(np.float32) / 255.0
                
                bg_cool = cv2.convertScaleAbs(image, alpha=0.4, beta=0)
                bg_cool[:, :, 0] = cv2.add(bg_cool[:, :, 0], 25)
                
                mask_f_expanded = mask_f[:, :, np.newaxis]
                image = (bg_cool * (1.0 - mask_f_expanded) + thermal * mask_f_expanded).astype(np.uint8)
                background = cv2.convertScaleAbs(image, alpha=0.3, beta=0)

            # --- EFFECT 7: Particle Orbit ---
            elif state.active_effect == 7 and results.hand_landmarks:
                for hand_idx, hand in enumerate(results.hand_landmarks):
                    cx = int(hand[9].x * state.w)
                    cy = int(hand[9].y * state.h)
                    
                    vel = 0.0
                    for prev_id, prev_loc in state.prev_wrists.items():
                        dist = math.hypot(cx - prev_loc[0], cy - prev_loc[1])
                        if dist < 180:
                            vel = dist
                            break
                            
                    pulse_r = int(12 + math.sin(time.time() * 12) * 5)
                    cv2.circle(canvas, (cx, cy), pulse_r, color, 1, cv2.LINE_AA)
                    cv2.circle(canvas, (cx, cy), pulse_r + 6, color, 2, cv2.LINE_AA)
                    
                    if len(state.orbit_particles) < 120:
                        for _ in range(3):
                            angle = np.random.uniform(0, 2 * math.pi)
                            radius = np.random.uniform(25, 90)
                            speed = np.random.uniform(0.04, 0.12) + (vel * 0.003)
                            if np.random.rand() > 0.5:
                                speed = -speed
                            life = np.random.uniform(0.5, 1.0)
                            color_offset = np.random.randint(-20, 20)
                            state.orbit_particles.append([cx, cy, angle, radius, speed, life, color_offset])
                
                new_orbit_parts = []
                for op in state.orbit_particles:
                    cx, cy, o_angle, o_radius, o_speed, o_life, o_offset = op
                    o_angle += o_speed
                    o_life -= 0.02
                    o_radius += math.sin(time.time() * 3) * 0.5
                    
                    px = int(cx + math.cos(o_angle) * o_radius)
                    py = int(cy + math.sin(o_angle) * o_radius)
                    
                    if o_life > 0 and 0 <= px < state.w and 0 <= py < state.h:
                        p_color = (max(0, min(255, color[0] + o_offset)),
                                   max(0, min(255, color[1] + o_offset)),
                                   max(0, min(255, color[2] + o_offset)))
                        
                        r = int(o_life * 5) + 1
                        cv2.circle(canvas, (px, py), r, p_color, -1)
                        cv2.circle(canvas, (px, py), r + 2, (255, 255, 255), 1, cv2.LINE_AA)
                        new_orbit_parts.append([cx, cy, o_angle, o_radius, o_speed, o_life, o_offset])
                state.orbit_particles = new_orbit_parts[-150:]

            # --- EFFECT 8: Digital Rain Aura ---
            elif state.active_effect == 8 and results.hand_landmarks:
                for hand in results.hand_landmarks:
                    if np.random.rand() > 0.25:
                        joint_idx = np.random.randint(0, 21)
                        jx = int(hand[joint_idx].x * state.w)
                        jy = int(hand[joint_idx].y * state.h)
                        
                        char = random.choice("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ#@$%&*")
                        speed = np.random.uniform(1.5, 4.0)
                        life = np.random.uniform(0.6, 1.2)
                        g_color = (np.random.randint(50, 100), np.random.randint(200, 255), np.random.randint(50, 150))
                        state.digital_chars.append([jx, jy, char, speed, life, g_color])
                
                new_chars = []
                for dc in state.digital_chars:
                    dx, dy, d_char, d_speed, d_life, d_color = dc
                    dy -= d_speed
                    d_life -= 0.03
                    
                    if d_life > 0 and dy > 0:
                        scale = d_life * 0.45
                        cv2.putText(canvas, d_char, (int(dx), int(dy)), 
                                    cv2.FONT_HERSHEY_SIMPLEX, scale, d_color, 1, cv2.LINE_AA)
                        new_chars.append([dx, dy, d_char, d_speed, d_life, d_color])
                state.digital_chars = new_chars[-120:]

            # --- NEW EFFECT 9: Goku Power Core (Super Saiyan / Kamehameha) ---
            elif state.active_effect == 9 and results.hand_landmarks:
                # 9.1: Golden Fiery Aura rising from hand joints
                for hand in results.hand_landmarks:
                    for lm in hand:
                        lx = int(lm.x * state.w)
                        ly = int(lm.y * state.h)
                        
                        # Spawn 1 golden/red fiery particle
                        if np.random.rand() > 0.4:
                            vx = np.random.uniform(-1.5, 1.5)
                            vy = np.random.uniform(-5.0, -2.0)
                            life = np.random.uniform(0.4, 0.8)
                            # Gradient fiery color shift (Red -> Yellow -> White)
                            f_color = (0, np.random.randint(120, 220), 255) # BGR: Golden Yellow
                            state.goku_particles.append([lx, ly, vx, vy, life, f_color])
                            
                # Update & draw golden flame particles
                new_goku_parts = []
                for gp in state.goku_particles:
                    gx, gy, g_vx, g_vy, g_life, g_color = gp
                    gx += g_vx
                    gy += g_vy
                    g_life -= 0.03
                    
                    if g_life > 0 and 0 <= gx < state.w and 0 <= gy < state.h:
                        r = int(g_life * 8) + 1
                        # Shift color to white/yellow as it ages
                        if g_life < 0.3:
                            current_color = (130, 230, 255) # Light golden
                        elif g_life < 0.15:
                            current_color = (255, 255, 255) # White hot core
                        else:
                            current_color = g_color
                        cv2.circle(canvas, (int(gx), int(gy)), r, current_color, -1)
                        new_goku_parts.append([gx, gy, g_vx, g_vy, g_life, g_color])
                state.goku_particles = new_goku_parts[-200:]

                # 9.2: Kamehameha sphere forming between hands if they are close
                if num_detected == 2:
                    hand1 = results.hand_landmarks[0]
                    hand2 = results.hand_landmarks[1]
                    cx1 = int(hand1[9].x * state.w)
                    cy1 = int(hand1[9].y * state.h)
                    cx2 = int(hand2[9].x * state.w)
                    cy2 = int(hand2[9].y * state.h)
                    
                    mid_x = (cx1 + cx2) // 2
                    mid_y = (cy1 + cy2) // 2
                    dist = math.hypot(cx1 - cx2, cy1 - cy2)
                    
                    # If hands are relatively close, Kamehameha energy ball triggers!
                    if dist < 240:
                        # Draw Energy ball with pulsing size
                        energy_radius = int((240 - dist) * 0.35 + math.sin(time.time() * 20) * 8)
                        energy_radius = max(10, energy_radius)
                        
                        # Visual Core (white hot cyan)
                        cv2.circle(canvas, (mid_x, mid_y), energy_radius, (255, 255, 255), -1)
                        cv2.circle(canvas, (mid_x, mid_y), energy_radius + 4, (255, 220, 160), 2, cv2.LINE_AA) # Light blue outer
                        cv2.circle(canvas, (mid_x, mid_y), energy_radius + 12, (255, 180, 80), 1, cv2.LINE_AA) # Cyan corona
                        
                        # Crackling inner lightning in the energy ball
                        for _ in range(3):
                            rx = mid_x + random.randint(-energy_radius, energy_radius)
                            ry = mid_y + random.randint(-energy_radius, energy_radius)
                            cv2.circle(canvas, (rx, ry), random.randint(2, 5), (255, 255, 255), -1)
                            
                        # Electrical charge arcs from both index fingers into the core!
                        h1_tip = (int(hand1[8].x * state.w), int(hand1[8].y * state.h))
                        h2_tip = (int(hand2[8].x * state.w), int(hand2[8].y * state.h))
                        
                        draw_lightning(canvas, h1_tip, (mid_x, mid_y), color=(255, 200, 100), thickness=2, displace=10)
                        draw_lightning(canvas, h1_tip, (mid_x, mid_y), color=(255, 255, 255), thickness=1, displace=10)
                        draw_lightning(canvas, h2_tip, (mid_x, mid_y), color=(255, 200, 100), thickness=2, displace=10)
                        draw_lightning(canvas, h2_tip, (mid_x, mid_y), color=(255, 255, 255), thickness=1, displace=10)

                        # Trigger audio synth sweep once per 45 frames when hands get close
                        if state.goku_sound_cooldown <= 0:
                            play_kamehameha_charge()
                            state.goku_sound_cooldown = 45
                            state.set_notification("✨ KAMEHAMEHA! ✨")
                
                if state.goku_sound_cooldown > 0:
                    state.goku_sound_cooldown -= 1

            # --- RENDER HAND JOINT OVERLAYS ---
            # Render internal skeleton within each hand independently (No lines between the hands)
            if state.active_effect != 6: # Skip joint overlays in thermal view to keep look clean
                if results.hand_landmarks:
                    # Update pinch/zoom/grab logic per first hand
                    first_hand = results.hand_landmarks[0] if len(results.hand_landmarks) > 0 else None
                    pd = pinch_distance(first_hand) if first_hand is not None else None
                    # Smooth zoom factor (use normalized landmark distances)
                    if pd is not None and state.zoom_enabled:
                        # pd is normalized (0..1) because landmarks are in normalized coords
                        target_zoom = 1.0 + max(0.0, (0.25 - pd)) * 6.0
                        # clamp
                        target_zoom = max(1.0, min(3.0, target_zoom))
                        state.zoom_factor = state.zoom_factor * 0.85 + target_zoom * 0.15
                        # if very close, grab the cube
                        if pd < 0.03:
                            state.grabbed = True
                        else:
                            state.grabbed = False

                    for hand in results.hand_landmarks:
                        # Draw skeletal lines only if not hidden by user
                        if not state.hide_hand_lines:
                                for start_idx, end_idx in HAND_CONNECTIONS:
                                    # Optionally suppress palm lines when cube or zoom active
                                    if (state.enable_cube or state.zoom_enabled) and (start_idx in PALM_INDICES or end_idx in PALM_INDICES):
                                        continue
                                    pt1 = (int(hand[start_idx].x * state.w), int(hand[start_idx].y * state.h))
                                    pt2 = (int(hand[end_idx].x * state.w), int(hand[end_idx].y * state.h))
                                    cv2.line(canvas, pt1, pt2, color=(255, 255, 255), thickness=1, lineType=cv2.LINE_AA)
                                    cv2.line(canvas, pt1, pt2, color=color, thickness=2, lineType=cv2.LINE_AA)
                        
                        for landmark in hand:
                            x, y = int(landmark.x * state.w), int(landmark.y * state.h)
                            cv2.circle(canvas, (x, y), 2, (255, 255, 255), -1)
                            cv2.circle(canvas, (x, y), 5, color, 1, cv2.LINE_AA)

                    # Cube overlay and gesture manipulation
                    if state.enable_cube and first_hand is not None:
                        # Anchor cube to the wrist/palm (use landmark 0 or 9 if available)
                        ref_idx = 9 if len(first_hand) > 9 else 0
                        cx = int(first_hand[ref_idx].x * state.w)
                        cy = int(first_hand[ref_idx].y * state.h)

                        # If grabbed, update cube position to follow index fingertip and allow rotation by motion
                        if state.grabbed:
                            ix = int(first_hand[8].x * state.w)
                            iy = int(first_hand[8].y * state.h)
                            # update position and compute velocity for inertia
                            if state.prev_index_pos is not None:
                                pdx = ix - state.prev_index_pos[0]
                                pdy = iy - state.prev_index_pos[1]
                                # set immediate velocities (pixels/frame)
                                state.cube['vel']['x'] = pdx * 0.72
                                state.cube['vel']['y'] = pdy * 0.72
                                # rotation deltas
                                state.cube['vel']['rot_y'] = pdx * 0.9
                                state.cube['vel']['rot_x'] = pdy * 0.7
                                # apply rotation
                                state.cube['rot_y'] = (state.cube['rot_y'] + pdx * 0.6) % 360
                                state.cube['rot_x'] = (state.cube['rot_x'] + pdy * 0.45) % 360
                            state.cube['pos'] = (ix, iy)
                            state.prev_index_pos = (ix, iy)
                        else:
                            # gently follow the palm and apply inertia
                            px, py = state.cube['pos']
                            nx = int(cx)
                            ny = int(cy)
                            # inertial motion
                            px = px + state.cube['vel']['x']
                            py = py + state.cube['vel']['y']
                            state.cube['pos'] = (int(px * 0.95 + nx * 0.05), int(py * 0.95 + ny * 0.05))
                            # apply damping to velocities and rotation
                            state.cube['vel']['x'] *= state.cube.get('damping', 0.90)
                            state.cube['vel']['y'] *= state.cube.get('damping', 0.90)
                            state.cube['vel']['rot_x'] *= state.cube.get('damping', 0.90)
                            state.cube['vel']['rot_y'] *= state.cube.get('damping', 0.90)
                            state.cube['rot_x'] = (state.cube['rot_x'] + state.cube['vel']['rot_x']) % 360
                            state.cube['rot_y'] = (state.cube['rot_y'] + state.cube['vel']['rot_y']) % 360
                            state.prev_index_pos = None

                        # Two-hand scaling: if two hands present, scale cube smoothly by distance
                        if num_detected == 2:
                            h1 = results.hand_landmarks[0]
                            h2 = results.hand_landmarks[1]
                            x1, y1 = int(h1[0].x * state.w), int(h1[0].y * state.h)
                            x2, y2 = int(h2[0].x * state.w), int(h2[0].y * state.h)
                            hands_dist = math.hypot(x2 - x1, y2 - y1)
                            # map hand separation to scale factor around base size
                            base = state.cube['base_size']
                            target_size = int(max(24, min(state.w, state.h) * 0.6, base * (hands_dist / (state.w * 0.3))))
                            # smooth resize
                            cur = state.cube['size']
                            state.cube['size'] = int(cur * 0.85 + target_size * 0.15)
                        else:
                            # apply manual scale multiplier
                            desired = int(state.cube['base_size'] * state.cube.get('scale', 1.0))
                            state.cube['size'] = int(state.cube['size'] * 0.85 + desired * 0.15)

                        # Snap-to-palm if close enough when not grabbed
                        if not state.grabbed:
                            px, py = state.cube['pos']
                            dist_to_palm = math.hypot(px - cx, py - cy)
                            if dist_to_palm < state.cube.get('snap_threshold', 40):
                                # lerp toward palm
                                sp = state.cube.get('snap_speed', 0.18)
                                nxp = int(px * (1.0 - sp) + cx * sp)
                                nyp = int(py * (1.0 - sp) + cy * sp)
                                state.cube['pos'] = (nxp, nyp)
                                # reduce velocities
                                state.cube['vel']['x'] *= 0.6
                                state.cube['vel']['y'] *= 0.6

                        # Draw the cube with rotation and current scale
                        _set_canvas_rotation(canvas, state.cube.get('rot_x', 0.0), state.cube.get('rot_y', 0.0))
                        draw_cube(canvas, state.cube['pos'], state.cube['size'], state.cube.get('angle', 0.0))
            
            # --- RENDER GLOW & MERGE IMAGES ---
            glow_start = time.perf_counter()
            if state.glow_mode == 0:
                small_canvas = cv2.resize(canvas, (state.w // 4, state.h // 4), interpolation=cv2.INTER_LINEAR)
                glow_small = cv2.GaussianBlur(small_canvas, (5, 5), 0)
                glow = cv2.resize(glow_small, (state.w, state.h), interpolation=cv2.INTER_LINEAR)
                canvas_glow = cv2.addWeighted(canvas, 0.8, glow, 1.2, 0)
                final_image = cv2.addWeighted(background, 1.0, canvas_glow, 1.0, 0)
            elif state.glow_mode == 1:
                glow = cv2.GaussianBlur(canvas, (19, 19), 0)
                canvas_glow = cv2.addWeighted(canvas, 0.8, glow, 1.2, 0)
                final_image = cv2.addWeighted(background, 1.0, canvas_glow, 1.0, 0)
            else:
                final_image = cv2.addWeighted(background, 1.0, canvas, 1.0, 0)
                
            glow_time = (time.perf_counter() - glow_start) * 1000
            effect_time = (time.perf_counter() - effect_render_start) * 1000

            # --- RENDER ON-SCREEN INTERACTIVE BUTTONS ---
            # 1. Capture Image Button (Icon representation + text)
            # Box coords: [w - 110, 15] to [w - 65, 45]
            draw_semi_transparent_rect(final_image, (state.w - 110, 15), (state.w - 65, 45), (40, 40, 45), 0.7)
            cv2.rectangle(final_image, (state.w - 110, 15), (state.w - 65, 45), (150, 150, 170), 1, cv2.LINE_AA)
            # Camera icon drawing (a little square body + small flash circle + lens circle)
            cv2.rectangle(final_image, (state.w - 100, 24), (state.w - 75, 40), (220, 220, 230), 1, cv2.LINE_AA)
            cv2.circle(final_image, (state.w - 87, 32), 4, (120, 240, 120), -1, cv2.LINE_AA)
            
            # 2. Record Video Button (Red record indicator circle + text)
            # Box coords: [w - 55, 15] to [w - 10, 45]
            draw_semi_transparent_rect(final_image, (state.w - 55, 15), (state.w - 10, 45), (40, 40, 45), 0.7)
            cv2.rectangle(final_image, (state.w - 55, 15), (state.w - 10, 45), (150, 150, 170), 1, cv2.LINE_AA)
            if state.is_recording:
                # Blinking red dot when recording
                dot_color = (0, 0, 255) if int(time.time() * 2) % 2 == 0 else (50, 50, 80)
                cv2.circle(final_image, (state.w - 32, 30), 6, dot_color, -1, cv2.LINE_AA)
            else:
                # Solid dark red circle
                cv2.circle(final_image, (state.w - 32, 30), 6, (0, 0, 150), -1, cv2.LINE_AA)

            # --- DIAGNOSTIC HUD OVERLAY ---
            if state.show_hud:
                draw_semi_transparent_rect(final_image, (10, 10), (320, 160), (18, 18, 22), 0.75)
                cv2.rectangle(final_image, (10, 10), (320, 160), (80, 80, 95), 1, cv2.LINE_AA)
                
                effect_name = EFFECT_NAMES.get(state.active_effect, "None")
                cv2.putText(final_image, f"Mode: {effect_name}", (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (99, 102, 241), 1, cv2.LINE_AA)
                
                cv2.putText(final_image, f"FPS: {current_fps:.1f} Hz", (20, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (230, 230, 240), 1, cv2.LINE_AA)
                cv2.putText(final_image, f"Inference: {inference_time:.1f} ms", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 210), 1, cv2.LINE_AA)
                cv2.putText(final_image, f"Effect/Blur: {effect_time:.1f} / {glow_time:.1f} ms", (20, 88), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 210), 1, cv2.LINE_AA)
                
                glow_status = "Downsampled Blur" if state.glow_mode == 0 else ("Direct Blur" if state.glow_mode == 1 else "Glow Disabled")
                cv2.putText(final_image, f"Glow: {glow_status}", (20, 108), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (170, 230, 180), 1, cv2.LINE_AA)
                cv2.putText(final_image, f"Resolution: {state.w}x{state.h}", (20, 126), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 220, 240), 1, cv2.LINE_AA)
                cv2.putText(final_image, f"Delegate: CPU (TFLite XNNPACK)", (20, 144), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (240, 200, 150), 1, cv2.LINE_AA)
                
                # Bottom info instruction text bar
                draw_semi_transparent_rect(final_image, (0, final_image.shape[0] - 25), (final_image.shape[1], final_image.shape[0]), (10, 10, 12), 0.85)
                cv2.putText(final_image, "Controls: [0-9] Effects | [R] Res | [B] Glow | [F] Full | [C] Photo | [V] Rec | [Q] Exit", 
                            (12, final_image.shape[0] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 210), 1, cv2.LINE_AA)

            # --- POPUP NOTIFICATIONS SYSTEM ---
            if time.time() < state.notification_time:
                cv2.putText(final_image, state.notification_text, 
                            (state.w // 2 - 120, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (50, 255, 50), 2, cv2.LINE_AA)

            # --- VIDEO WRITER FRAME CAPTURE ---
            if state.is_recording and state.video_writer:
                state.video_writer.write(final_image)
                # Draw minor REC indicator outside the HUD
                cv2.putText(final_image, "● RECORDING", (state.w - 145, final_image.shape[0] - 38),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

            # --- PHOTO CAPTURE TRIGGER ---
            if state.trigger_capture:
                state.trigger_capture = False
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"captures/capture_{timestamp}.png"
                cv2.imwrite(filename, final_image)
                state.set_notification("Photo Saved!")
                play_shutter_sound()

            # --- VIDEO RECORDING TRIGGER ---
            if state.trigger_record:
                state.trigger_record = False
                state.is_recording = not state.is_recording
                if state.is_recording:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"captures/recording_{timestamp}.avi"
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    state.video_writer = cv2.VideoWriter(filename, fourcc, 22.0, (state.w, state.h))
                    state.set_notification("Recording Started!")
                    play_rec_start()
                else:
                    if state.video_writer:
                        state.video_writer.release()
                        state.video_writer = None
                    state.set_notification("Video Saved!")
                    play_rec_stop()

            # Render output (apply digital pinch-zoom if active)
            display_image = final_image
            try:
                if state.zoom_enabled and state.zoom_factor > 1.02:
                    cx, cy = state.cube.get('pos', (state.w // 2, state.h // 2))
                    crop_w = int(state.w / state.zoom_factor)
                    crop_h = int(state.h / state.zoom_factor)
                    x1 = max(0, int(cx - crop_w // 2))
                    y1 = max(0, int(cy - crop_h // 2))
                    x2 = min(state.w, x1 + crop_w)
                    y2 = min(state.h, y1 + crop_h)
                    crop = final_image[y1:y2, x1:x2]
                    if crop.shape[0] > 0 and crop.shape[1] > 0:
                        display_image = cv2.resize(crop, (state.w, state.h), interpolation=cv2.INTER_LINEAR)
            except Exception:
                display_image = final_image

            cv2.imshow(window_name, display_image)
            
            # --- KEYBOARD CONTROLS PROCESSING ---
            key = cv2.waitKey(5) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('d'):
                state.show_hud = not state.show_hud
            elif key == ord('b'):
                state.glow_mode = (state.glow_mode + 1) % 3
            elif key == ord('f'):
                state.fullscreen = not state.fullscreen
                if state.fullscreen:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                else:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            elif key == ord('c'):
                state.trigger_capture = True
            elif key == ord('v'):
                state.trigger_record = True
            elif key == ord('r'):
                # Toggle Resolution
                new_w, new_h = (1280, 720) if state.w == 640 else (640, 360)
                
                # Release and re-open to prevent MSMF stream failure crashes on Windows
                cap.release()
                cap = cv2.VideoCapture(camera_index)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, new_w)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, new_h)
                
                # Flush camera queue buffer securely checking success
                for _ in range(5):
                    ret, _ = cap.read()
                    if not ret:
                        break
                        
                # Update status
                state.w = new_w
                state.h = new_h
                # Clear state and pre-allocate
                state.init_ripple_maps(new_w, new_h)
                canvas = np.zeros((new_h, new_w, 3), dtype=np.uint8)
                state.ghost_buffer.clear()
                state.particles.clear()
                state.orbit_particles.clear()
                state.digital_chars.clear()
                state.goku_particles.clear()
                
                cv2.setMouseCallback(window_name, mouse_callback, state)
            elif key == ord('o'):
                # Toggle hand outline/lines
                state.hide_hand_lines = not state.hide_hand_lines
                state.set_notification(f"Hand Lines {'Hidden' if state.hide_hand_lines else 'Shown'}")
            elif key == ord('m'):
                # Toggle faux 3D cube overlay
                state.enable_cube = not state.enable_cube
                state.set_notification(f"3D Cube {'Enabled' if state.enable_cube else 'Disabled'}")
            elif key == ord('p'):
                # Toggle pinch zoom
                state.zoom_enabled = not state.zoom_enabled
                state.set_notification(f"Pinch Zoom {'Enabled' if state.zoom_enabled else 'Disabled'}")
            elif key == ord('w'):
                # Toggle websocket broadcaster
                if ws_server is not None:
                    if not state.ws_running:
                        try:
                            ws_server.start(host='0.0.0.0', port=state.ws_port)
                            state.ws_running = True
                            state.set_notification(f"WebSocket server started on :{state.ws_port}")
                        except Exception as e:
                            state.set_notification(f"WS start failed: {e}")
                    else:
                        # stopping is a no-op in simple server, flip flag
                        state.ws_running = False
                        ws_server.latest_landmarks = None
                        state.set_notification("WebSocket server stopped")
                else:
                    state.set_notification("WebSocket module unavailable")
            elif key == ord('['):
                # Rotate cube left around Y-axis
                state.cube['rot_y'] = (state.cube['rot_y'] - 10) % 360
            elif key == ord(']'):
                # Rotate cube right around Y-axis
                state.cube['rot_y'] = (state.cube['rot_y'] + 10) % 360
            elif key == ord(';'):
                # Rotate cube up around X-axis
                state.cube['rot_x'] = (state.cube['rot_x'] - 10) % 360
            elif key == ord('\''):
                # Rotate cube down around X-axis
                state.cube['rot_x'] = (state.cube['rot_x'] + 10) % 360
            elif key == ord('='):
                # manual scale up
                state.cube['scale'] = min(4.0, state.cube.get('scale', 1.0) * 1.12)
            elif key == ord('-'):
                # manual scale down
                state.cube['scale'] = max(0.3, state.cube.get('scale', 1.0) / 1.12)
            elif ord('0') <= key <= ord('9'):
                state.active_effect = key - ord('0')

            # Calculate FPS
            fps_frame_count += 1
            elapsed = time.time() - fps_prev_time
            if elapsed >= 0.5:
                current_fps = fps_frame_count / elapsed
                fps_frame_count = 0
                fps_prev_time = time.time()
                
    cap.release()
    if state.video_writer:
        state.video_writer.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()