import smtplib
from email.message import EmailMessage
import ssl
import os
import certifi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SENDER_EMAIL = os.getenv("EMAIL_SENDER")
SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("EMAIL_RECEIVER")

def send_intrusion_alert(entry_time, snapshot_path):
    try:
        msg = EmailMessage()
        msg["Subject"] = "🚨 Intrusion Alert Detected"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL

        msg.set_content(
            f"""
INTRUSION DETECTED

Time: {entry_time.strftime('%Y-%m-%d %H:%M:%S')}
Camera: cam_demo_01

See attached snapshot for evidence.
"""
        )

        with open(snapshot_path, "rb") as f:
            img_data = f.read()

        msg.add_attachment(
            img_data,
            maintype="image",
            subtype="jpeg",
            filename=os.path.basename(snapshot_path),
        )

        context = ssl.create_default_context(cafile=certifi.where())

        print("[EMAIL] Connecting to SMTP server...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)#type:ignore
            server.send_message(msg)
        
        print(f"[EMAIL] Alert sent successfully to {RECEIVER_EMAIL}")

    except Exception as e:
        print(f"❌ [EMAIL FAILED] Could not send alert: {e}")