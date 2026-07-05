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

# Indices corresponding to MediaPipe Hand landmarks
FINGER_TIPS = [4, 8, 12, 16, 20]     # THUMB_TIP, INDEX_FINGER_TIP, etc.
FINGER_JOINTS = [3, 7, 11, 15, 19]   # THUMB_IP, INDEX_FINGER_DIP, etc.


def choose_camera():
    selected_camera = [0]
    
    root = tk.Tk()
    root.title("Antigravity - Select Camera")
    root.geometry("350x300")
    # center window
    root.eval('tk::PlaceWindow . center')
    
    lbl = ttk.Label(root, text="Scanning for available cameras...", font=("Arial", 11))
    lbl.pack(pady=20)
    
    btn_frame = ttk.Frame(root)
    btn_frame.pack(fill=tk.BOTH, expand=True, padx=20)
    
    def on_select(idx):
        selected_camera[0] = idx
        root.destroy()
        
    def scan_cams():
        available = []
        # Check first 5 index spots
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available.append(i)
                cap.release()
            else:
                cap.release()
                
        # Send results back to main thread to update GUI
        root.after(0, build_ui, available)
        
    def build_ui(available):
        lbl.config(text="Select the camera to use bitch!!:")
        if not available:
            lbl.config(text="No cameras found! Trying default 0...")
            btn = ttk.Button(btn_frame, text="Continue (Camera 0)", command=lambda: on_select(0))
            btn.pack(pady=5, fill=tk.X)
            return
            
        for idx in available:
            name = f"Camera {idx}"
            if idx == 0:
                name += " (Built in Camera)"
            else:
                name += " (Webcam / Droidcam)"
            btn = ttk.Button(btn_frame, text=name, command=lambda i=idx: on_select(i))
            btn.pack(pady=5, fill=tk.X)
            
    # Start scanning in a thread to keep GUI responsive
    threading.Thread(target=scan_cams, daemon=True).start()
    
    # If closed with X, default to 0
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

def main():
    camera_index = choose_camera()
    cap = cv2.VideoCapture(camera_index)
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=2,
        min_hand_detection_confidence=0.6,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.6,
        running_mode=vision.RunningMode.IMAGE
    )

    with vision.HandLandmarker.create_from_options(options) as landmarker:
        print("Starting camera... Press 'q' to quit.")
        
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                break

            image = cv2.flip(image, 1)
            h, w, _ = image.shape

            background = cv2.convertScaleAbs(image, alpha=0.3, beta=0)
            
            canvas = np.zeros_like(image, dtype=np.uint8)

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
            
            results = landmarker.detect(mp_image)

            if results.hand_landmarks and len(results.hand_landmarks) == 2:
                hand1 = results.hand_landmarks[0]
                hand2 = results.hand_landmarks[1]
                
                h1_wrist = (int(hand1[0].x * w), int(hand1[0].y * h))
                h2_wrist = (int(hand2[0].x * w), int(hand2[0].y * h))
                hands_distance = math.hypot(h1_wrist[0] - h2_wrist[0], h1_wrist[1] - h2_wrist[1])
                
                color = get_dynamic_color(hands_distance, max_distance=w*0.8)

                for hand in [hand1, hand2]:
                    for landmark in hand:
                        x, y = int(landmark.x * w), int(landmark.y * h)
                        cv2.circle(canvas, (x, y), 2, (255, 255, 255), -1)
                        cv2.circle(canvas, (x, y), 6, color, 2)

                for tip_idx in FINGER_TIPS:
                    h1_tip = (int(hand1[tip_idx].x * w), int(hand1[tip_idx].y * h))
                    h2_tip = (int(hand2[tip_idx].x * w), int(hand2[tip_idx].y * h))

                    cv2.line(canvas, h1_tip, h2_tip, color=(255, 255, 255), thickness=1, lineType=cv2.LINE_AA)
                    cv2.line(canvas, h1_tip, h2_tip, color=color, thickness=2, lineType=cv2.LINE_AA)
            
            elif results.hand_landmarks:
                color = get_dynamic_color(200, max_distance=w)
                for hand in results.hand_landmarks:
                    for landmark in hand:
                        x, y = int(landmark.x * w), int(landmark.y * h)
                        cv2.circle(canvas, (x, y), 2, (255, 255, 255), -1)
                        cv2.circle(canvas, (x, y), 6, color, 2)

            glow = cv2.GaussianBlur(canvas, (19, 19), 0)
            canvas_glow = cv2.addWeighted(canvas, 0.8, glow, 1.2, 0)
            final_image = cv2.addWeighted(background, 1.0, canvas_glow, 1.0, 0)
            
            cv2.imshow('MediaPipe Hand Tricks - Press Q to Exit', final_image)
            
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
                
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
