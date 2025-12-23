import cv2
import time
import geocoder
import mediapipe as mp
from twilio.rest import Client

# =========================
# TWILIO CONFIGURATION
# =========================
ACCOUNT_SID = "AC2f446bcf1764dd16a333b4cb93e95267"
AUTH_TOKEN = "754ae632bf42b9162b1736b8d8d87788N"

FROM_WHATSAPP = "whatsapp:+14155238886"
TO_WHATSAPP = "whatsapp:+919449839200"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# =========================
# LOCATION FUNCTION
# =========================
def get_live_location():
    g = geocoder.ip('me')
    if g.latlng:
        lat, lon = g.latlng
        return f"https://maps.google.com/?q={lat},{lon}"
    return "Location not available"

# =========================
# SEND SOS ALERT
# =========================
def send_sos_alert():
    location = get_live_location()
    message = f"""🚨 SOS EMERGENCY ALERT 🚨
Emergency gesture detected!

📍 Live Location:
{location}

🕒 Time:
{time.ctime()}

Please respond immediately.
"""
    client.messages.create(
        body=message,
        from_=FROM_WHATSAPP,
        to=TO_WHATSAPP
    )
    print("SOS alert sent")

# =========================
# HAND GESTURE SETUP
# =========================
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)
mp_draw = mp.solutions.drawing_utils

# =========================
# OPEN PALM DETECTION
# =========================
def is_open_palm(hand_landmarks):
    # Count extended fingers (simple heuristic)
    tips = [8, 12, 16, 20]      # finger tips
    pips = [6, 10, 14, 18]      # finger mid joints
    extended = 0

    for tip, pip in zip(tips, pips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            extended += 1

    # Thumb (horizontal check)
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        extended += 1

    return extended >= 4   # open palm if 4 or 5 fingers extended

# =========================
# MAIN LOOP
# =========================
cap = cv2.VideoCapture(0)
sos_sent = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    status_text = "STATUS: NORMAL"
    status_color = (0, 255, 0)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if is_open_palm(hand_landmarks) and not sos_sent:
                sos_sent = True
                send_sos_alert()
                status_text = "EMERGENCY DETECTED"
                status_color = (0, 0, 255)

    if sos_sent:
        status_text = "EMERGENCY DETECTED"
        status_color = (0, 0, 255)

    cv2.putText(frame, status_text, (40, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, status_color, 3)

    cv2.imshow("SmartShield – Gesture SOS", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
