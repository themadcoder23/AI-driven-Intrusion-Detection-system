import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

key_path = os.getenv("FIREBASE_KEY_PATH", "firebase_key.json")

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
        print("[FIREBASE] Connected successfully.")
    except Exception as e:
        print(f"❌ [FIREBASE ERROR] Could not initialize: {e}")

db = firestore.client()

def log_intrusion_event(event_data):
    try:
        db.collection("intrusion_events").add(event_data)
        print("[FIREBASE] Event logged to Firestore.")
    except Exception as e:
        print(f"❌ [FIREBASE WRITE FAILED] {e}")