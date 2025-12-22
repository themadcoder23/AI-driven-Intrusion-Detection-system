# AI-Based Restricted Zone Intrusion Detection

This project detects unauthorized human presence in restricted zones using computer vision and logs intrusion events to the cloud with real-time alerts.

## Features
- Human detection using YOLO
- User-defined restricted zone (ROI)
- False-alarm prevention using frame persistence
- Snapshot capture as visual evidence
- Firebase Firestore logging
- Email alerts on intrusion
- Cooldown logic to prevent alert spam

## Tech Stack
- Python
- OpenCV
- YOLO (Ultralytics)
- Google Firebase Firestore
- SMTP (Email alerts)

## System Flow
1. Capture video frame
2. Detect humans using YOLO
3. Check if detection lies inside restricted zone
4. Confirm intrusion after sustained presence
5. Capture snapshot
6. Log event to Firebase
7. Send alert email

## Google Service Used
- Firebase Firestore for centralized intrusion event logging

## Project Structure
.
├── main.py
├── roi.py
├── firebase_logger.py
├── alert_email.py
├── snapshots/
├── videos/
└── README.md

## Note
This implementation is designed to demonstrate a real-world security pipeline. Detection runs locally for low latency, while Firebase provides a reliable cloud audit trail.
