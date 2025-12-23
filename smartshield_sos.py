import time
import random
import geocoder
from twilio.rest import Client

# ================= TWILIO CONFIG =================
# IMPORTANT: Replace with YOUR Twilio credentials
ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
AUTH_TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

FROM_WHATSAPP = "whatsapp:+14155238886"   # Twilio WhatsApp Sandbox
TO_WHATSAPP = "whatsapp:+91YOURNUMBER"    # Emergency contact number

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# ================= LOCATION FUNCTION =================
def get_live_location():
    """
    Gets approximate live location using IP address.
    Returns Google Maps link.
    """
    try:
        g = geocoder.ip("me")
        if g.ok:
            lat, lon = g.latlng
            return f"https://www.google.com/maps?q={lat},{lon}"
        else:
            return "Location not available"
    except Exception:
        return "Location error"

# ================= SEND ALERT =================
def send_emergency_alert():
    location_link = get_live_location()

    message = (
        "🚨 SMARTSHIELD EMERGENCY ALERT 🚨\n"
        "Accident detected!\n"
        "Rider may require immediate medical assistance.\n\n"
        f"📍 Live Location:\n{location_link}"
    )

    client.messages.create(
        from_=FROM_WHATSAPP,
        to=TO_WHATSAPP,
        body=message
    )

    print("Emergency alert sent successfully.")

# ================= ACCIDENT DETECTION =================
def detect_accident():
    """
    Simulated accident detection.
    Replace with MPU6050 / mobile sensor logic later.
    """
    sensor_value = random.randint(1, 100)
    print("Sensor value:", sensor_value)

    if sensor_value > 95:   # accident threshold
        return True
    return False

# ================= MAIN PROGRAM =================
print("SmartShield Emergency Alert System Activated...")

alert_sent = False

while True:
    if detect_accident() and not alert_sent:
        print("Accident detected! Sending emergency alert...")
        send_emergency_alert()
        alert_sent = True
        break

    time.sleep(3)
