import cv2
import numpy as np
from ultralytics import YOLO  # type:ignore
from roi import select_roi
from datetime import datetime
import os
import threading
from firebase_logger import log_intrusion_event
from alert_email import send_intrusion_alert

# ---------------- CONFIG ----------------
VIDEO_PATH = "videos/main.mp4"  # Set to 0 for Webcam

CONFIRMATION_FRAMES = 10      # Frames to confirm it is a person (Sensitivity)
PATIENCE_FRAMES = 20          # Frames to wait before declaring "Intruder Gone" (Prevents flickering)
COOLDOWN_SECONDS = 60         # Cooldown between separate emails

# ---------------- SETUP ----------------
os.makedirs("snapshots", exist_ok=True)

# Load YOLO model

model = YOLO("yolov8n.pt")

# ---------------- HELPERS ----------------
def is_inside_roi(box, roi):
    x1, y1, x2, y2 = box
    # We check the "feet" point (bottom center) as it's the most accurate anchor for location
    feet_x = (x1 + x2) // 2
    feet_y = y2
    return cv2.pointPolygonTest(roi, (feet_x, feet_y), False) >= 0

def save_snapshot(frame, timestamp):
    filename = f"snapshots/intrusion_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
    cv2.imwrite(filename, frame)
    return filename

# ---------------- ROI SELECTION ----------------
cap = cv2.VideoCapture(VIDEO_PATH)
ret, first_frame = cap.read()
cap.release()

if not ret:
    print("ERROR: Cannot read video source")
    exit()

roi_polygon = select_roi(first_frame)
if roi_polygon is None:
    print("No ROI selected. Exiting.")
    exit()

# ---------------- VIDEO PROCESSING ----------------
cap = cv2.VideoCapture(VIDEO_PATH)

intrusion_active = False
entry_time = None
current_event = None

# Counters
frames_person_present = 0
frames_person_missing = 0
last_alert_time = None

frame_idx = 0

print("[SYSTEM] Monitoring started...")

while True:
    ret, frame = cap.read()
    if not ret:
        break # End of video or camera disconnect

    frame_idx += 1
    
    # 1. Draw ROI
    cv2.polylines(frame, [roi_polygon], True, (0, 255, 0), 2)

    person_detected_in_this_frame = False

    # 2. YOLO Inference
    results = model(frame, conf=0.4, classes=[0], verbose=False) # class 0 = person

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # Check if this specific person is inside the ROI
            if is_inside_roi((x1, y1, x2, y2), roi_polygon):
                person_detected_in_this_frame = True
                
                # Visuals
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, "INTRUDER", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # ---------------- LOGIC CORE ----------------
    
    # A. Confirmation Logic (Is there a person?)
    if person_detected_in_this_frame:
        frames_person_present += 1
        frames_person_missing = 0  # Reset "missing" counter because we see them
    else:
        frames_person_present = 0
        if intrusion_active:
            frames_person_missing += 1

    now = datetime.now()

    # B. Trigger Start of Intrusion
    if frames_person_present >= CONFIRMATION_FRAMES and not intrusion_active:
        
        # Check Cooldown
        if last_alert_time is None or (now - last_alert_time).total_seconds() > COOLDOWN_SECONDS:
            intrusion_active = True
            entry_time = now
            last_alert_time = now
            
            # Save Snapshot
            snapshot_path = save_snapshot(frame, entry_time)
            
            current_event = {
                "entry_time": entry_time,
                "snapshot": snapshot_path
            }

            print(f"🚨 [ALERT] Intrusion detected at {entry_time.strftime('%H:%M:%S')}")
            
            # THREADING: Send email in background so video doesn't freeze
            threading.Thread(target=send_intrusion_alert, args=(entry_time, snapshot_path)).start()

    # C. Trigger End of Intrusion (With Grace Period)
    # Only end intrusion if person has been missing for PATIENCE_FRAMES consecutively
    if intrusion_active and frames_person_missing >= PATIENCE_FRAMES:
        exit_time = datetime.now()
        duration = (exit_time - entry_time).total_seconds() # type: ignore

        print(f"✅ [CLEARED] Intruder left. Duration: {duration:.1f}s")

        current_event["exit_time"] = exit_time.isoformat() # type: ignore
        current_event["duration"] = duration # type: ignore
        
        event_payload = {
            "camera_id": "cam_demo_01",
            "entry_time": current_event["entry_time"].isoformat(), # type: ignore
            "exit_time": current_event["exit_time"],#type:ignore
            "duration_seconds": duration,
            "snapshot_path": current_event["snapshot"] # type: ignore
        }

        # THREADING: Log to Firebase in background
        threading.Thread(target=log_intrusion_event, args=(event_payload,)).start()

        # Reset states
        intrusion_active = False
        entry_time = None
        current_event = None
        frames_person_missing = 0

    # ---------------- OVERLAY ----------------
    status_color = (0, 0, 255) if intrusion_active else (0, 255, 0)
    status_text = "STATUS: INTRUDER DETECTED" if intrusion_active else "STATUS: SECURE"
    
    cv2.putText(frame, status_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
    cv2.imshow("Intruder Detection System", frame)

    if cv2.waitKey(1) & 0xFF == 27: # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()