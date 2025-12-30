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
VIDEO_PATH = "videos/final2.mp4"  # Set to 0 for Webcam

CONFIRMATION_FRAMES = 10      # Frames to officially trigger alert (Email/Firebase)
PATIENCE_FRAMES = 20          # Frames to wait before clearing the alert
COOLDOWN_SECONDS = 60         # Seconds between separate email alerts

# ---------------- SETUP ----------------
os.makedirs("snapshots", exist_ok=True)

# Load YOLO model (Nano is fastest for real-time)
model = YOLO("yolov8n.pt")

# ---------------- HELPERS ----------------
def is_inside_roi(box, roi):
    x1, y1, x2, y2 = box
    # Anchor point: Feet (bottom center)
    feet_x = (x1 + x2) // 2
    feet_y = y2
    return cv2.pointPolygonTest(roi, (feet_x, feet_y), False) >= 0

def save_snapshot(frame, timestamp):
    filename = f"snapshots/intrusion_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
    cv2.imwrite(filename, frame)
    return filename

# ---------------- INITIALIZATION ----------------
cap = cv2.VideoCapture(VIDEO_PATH)
ret, first_frame = cap.read()
if not ret:
    print("ERROR: Cannot read video source")
    exit()

# Select ROI on the first frame
roi_polygon = select_roi(first_frame)
if roi_polygon is None:
    print("No ROI selected. Exiting.")
    exit()

# Reset capture to start of video
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

# Global States
intrusion_alert_active = False # The "Official" alert state (Email sent)
entry_time = None
current_event = None
last_alert_time = None

# Counters
frames_person_present = 0
frames_person_missing = 0

print("[SYSTEM] Monitoring started. Press ESC to quit.")

# ---------------- PROCESSING LOOP ----------------
while True:
    ret, frame = cap.read()
    if not ret:
        break 

    # 1. Overlay ROI Boundary
    cv2.polylines(frame, [roi_polygon], True, (0, 255, 0), 2)

    # 2. YOLO Inference (Class 0 = Person)
    results = model(frame, conf=0.4, classes=[0], verbose=False)
    
    person_in_roi_right_now = False

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            if is_inside_roi((x1, y1, x2, y2), roi_polygon):
                person_in_roi_right_now = True
                # Visual box for detected intruder
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, "INTRUDER", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # ---------------- LOGIC CORE ----------------
    
    # Update counters based on current visibility
    if person_in_roi_right_now:
        frames_person_present += 1
        frames_person_missing = 0  
    else:
        frames_person_present = 0
        if intrusion_alert_active:
            frames_person_missing += 1

    now = datetime.now()

    # START: Official Intrusion Alert (Requires 10 frames of presence)
    if frames_person_present >= CONFIRMATION_FRAMES and not intrusion_alert_active:
        
        # Check Cooldown to avoid email spam
        if last_alert_time is None or (now - last_alert_time).total_seconds() > COOLDOWN_SECONDS:
            intrusion_alert_active = True
            entry_time = now
            last_alert_time = now
            
            snapshot_path = save_snapshot(frame, entry_time)
            current_event = {"entry_time": entry_time, "snapshot": snapshot_path}

            print(f"🚨 [ALERT] Intrusion officially logged at {entry_time.strftime('%H:%M:%S')}")
            
            # Send Email in background
            threading.Thread(target=send_intrusion_alert, args=(entry_time, snapshot_path)).start()

    # END: Official Intrusion Alert (Requires 20 frames of absence)
    if intrusion_alert_active and frames_person_missing >= PATIENCE_FRAMES:
        exit_time = datetime.now()
        duration = (exit_time - entry_time).total_seconds()

        print(f"✅ [CLEARED] Intruder left. Duration: {duration:.1f}s")

        event_payload = {
            "camera_id": "cam_demo_01",
            "entry_time": entry_time.isoformat(),
            "exit_time": exit_time.isoformat(),
            "duration_seconds": duration,
            "snapshot_path": current_event["snapshot"]
        }

        # Log to Firebase in background
        threading.Thread(target=log_intrusion_event, args=(event_payload,)).start()

        # Reset states
        intrusion_alert_active = False
        entry_time = None
        current_event = None
        frames_person_missing = 0

    # ---------------- UI OVERLAY ----------------
    # FIX: Status text depends on IMMEDIATE detection, not the confirmed alert state
    if person_in_roi_right_now:
        status_text = "STATUS: INTRUDER DETECTED"
        status_color = (0, 0, 255) # RED
    else:
        status_text = "STATUS: SECURE"
        status_color = (0, 255, 0) # GREEN
    
    cv2.putText(frame, status_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
    
    # Sub-label to show if the alert has been officially triggered/emailed
    if intrusion_alert_active:
        cv2.putText(frame, "ALERT ACTIVE (EMAIL SENT)", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    cv2.imshow("Intruder Detection System", frame)

    if cv2.waitKey(1) & 0xFF == 27: # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()