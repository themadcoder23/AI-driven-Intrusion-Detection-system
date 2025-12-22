# AI-Based Restricted Zone Intrusion Detection System

An AI-powered computer vision system that automatically detects unauthorized human presence inside restricted zones using video feeds. The system captures visual evidence, logs intrusion events to the cloud, and sends real-time alerts—eliminating the need for continuous manual CCTV monitoring.

---

## Key Features
- AI-based human detection using YOLO  
- Restricted Zone (ROI) based intrusion detection  
- False-alarm reduction using persistence logic  
- Snapshot capture as visual evidence  
- Cloud logging of intrusion events using **Google Firebase Firestore**  
- Real-time email alert notifications  
- Works with existing CCTV or surveillance-style video feeds  

---

## Tech Stack
- **Python**
- **OpenCV**
- **Ultralytics YOLOv8**
- **Google Firebase Firestore**
- SMTP (Email alerts)

---

## How It Works
1. Video feed is processed frame-by-frame  
2. AI model detects human presence  
3. Restricted zone (ROI) validation is applied  
4. Intrusion is confirmed after sustained presence  
5. Snapshot is captured as evidence  
6. Event metadata is logged to Firebase  
7. Email alert is sent to authorized personnel  

---

## Project Structure
```
intrusion-detection-system/
│
├── main.py                 # Main intrusion detection pipeline
├── roi.py                  # Restricted zone (ROI) selection
├── firebase_logger.py      # Firebase Firestore logging
├── alert_email.py          # Email alert service
├── snapshots/              # Saved intrusion snapshots (local)
├── videos/                 # Demo video input (local only)
├── yolov8n.pt              # YOLOv8 model weights
├── .gitignore
└── README.md
```

---

## Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/intrusion-detection-system.git
cd intrusion-detection-system
```

---

### 2️⃣ Install Dependencies
```bash
pip install ultralytics opencv-python firebase-admin
```

*(Python 3.9+ recommended)*

---

### 3️⃣ Firebase Setup (Required)
1. Create a Firebase project
2. Enable **Firestore Database**
3. Download the Firebase service account key  
4. Rename it to:
```
firebase_key.json
```
5. Place it in the project root


---

### 4️⃣ Configure Email Alerts
Edit `alert_email.py` and configure:
- Sender email
- App password (SMTP)
- Receiver email

*(Gmail App Password recommended)*

---

### 5️⃣ Run the System
```bash
python main.py
```

- Select the restricted zone (ROI) on the first frame  
- Press **ENTER** to confirm  
- System starts monitoring automatically  

---

## Demo & Testing
- Works with any surveillance-style video feed  
- Demo video used only for demonstration purposes  
- No proprietary footage included in the repository  

---

## Future Enhancements
- Live CCTV integration  
- Web-based monitoring dashboard  
- SMS / WhatsApp alerts  
- Multi-camera support  

---

## Disclaimer
This project is intended for educational and demonstration purposes only. Any video footage used in demos is publicly available or simulated and is not redistributed.

---

## Author
**Yax Patel**  
B.Tech CSE, Nirma University

---

## 🏁 License
This project is provided for educational use under open-source terms.

---

### FINAL NOTE
- No videos or credentials are included in this repository  
- Firebase key must be added locally to run the system  
