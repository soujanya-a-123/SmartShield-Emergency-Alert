import cv2
import numpy as np
import tensorflow as tf
import pyttsx3
import threading
from twilio.rest import Client # WhatsApp

# -----------------------------
# Twilio WhatsApp Credentials
# -----------------------------
TWILIO_SID = "AC2f446bcf1764dd16a333b4cb93e95267"
TWILIO_AUTH = "754ae632bf42b9162b1736b8d8d87788"

# WhatsApp numbers
TWILIO_WA_FROM = "whatsapp:+14155238886"   # Twilio Sandbox Number
TWILIO_WA_TO = "whatsapp:+919449839200"    # Your WhatsApp Number

# -----------------------------
# WhatsApp Alert Function
# -----------------------------
def send_whatsapp_alert():
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH)
        client.messages.create(
            from_=TWILIO_WA_FROM,
            to=TWILIO_WA_TO,
            body="⚠ ALERT: No Helmet Detected! Please wear your helmet."
        )
        print("📲 WhatsApp Alert Sent!")
    except Exception as e:
        print("WhatsApp Error:", e)


# -----------------------------
# Load Model
# -----------------------------
MODEL_PATH = "model.tflite"
LABELS_PATH = "labels.txt"

# Load labels
with open(LABELS_PATH, "r") as f:
    labels = [line.strip() for line in f.readlines()]

# Load TFLite model
interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

# -----------------------------
# Text-to-Speech Setup
# -----------------------------
engine = pyttsx3.init()
engine.setProperty("rate", 160)
engine.setProperty("volume", 1.0)

voice_lock = threading.Lock()
last_status = None  # Track last prediction


def speak_async(text):
    """Run TTS in background thread (non-blocking)."""
    def run():
        with voice_lock:
            engine.say(text)
            engine.runAndWait()
    threading.Thread(target=run).start()


# -----------------------------
# Start Webcam
# -----------------------------
cap = cv2.VideoCapture(0)
print("Camera started. Press 'q' to exit.")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # Resize for model
    img = cv2.resize(frame, (width, height))
    img = np.expand_dims(img, axis=0).astype(np.float32) / 255.0

    # Run prediction
    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()
    prediction = interpreter.get_tensor(output_details[0]['index'])[0]

    idx = np.argmax(prediction)
    label = labels[idx]
    confidence = prediction[idx] * 100

    # Helmet Logic
    if "helmet" in label.lower():
        status = "helmet"
        msg = "Helmet detected - Safe ride ✔"
        color = (0, 255, 0)
    else:
        status = "no_helmet"
        msg = "No Helmet Detected - Please Wear Helmet ❗"
        color = (0, 0, 255)

    # -----------------------------
    # Voice + WhatsApp Alert
    # (Trigger ONLY on state change)
    # -----------------------------
    if status != last_status:
        if status == "helmet":
            speak_async("Helmet detected. Safe ride.")
        else:
            speak_async("No helmet detected. Please wear your helmet.")
            send_whatsapp_alert()   # Send WhatsApp alert here

        last_status = status

    # -----------------------------
    # Display Output
    # -----------------------------
    cv2.putText(frame, f"{label} ({confidence:.1f}%)",
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.putText(frame, msg,
                (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    cv2.imshow("Helmet Detection - Teachable Machine", frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting...")
        break

cap.release()
cv2.destroyAllWindows()
