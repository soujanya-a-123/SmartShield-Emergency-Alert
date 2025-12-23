import time
import geocoder
from twilio.rest import Client

# =========================
# TWILIO CONFIGURATION
# =========================
ACCOUNT_SID = "AC2f446bcf1764dd16a333b4cb93e95267"
AUTH_TOKEN = "754ae632bf42b9162b1736b8d8d87788"

FROM_WHATSAPP = "whatsapp:+14155238886"   # Twilio WhatsApp sandbox
TO_WHATSAPP = "whatsapp:+919449839200"    # Emergency contact

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# =========================
# GET LIVE LOCATION
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
Rider needs immediate help.

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
    print("SOS alert sent successfully.")

# =========================
# MAIN
# =========================
print("SMARTSHIELD SOS SYSTEM")
print("Press 's' to send SOS alert")
print("Press 'q' to quit")

while True:
    key = input("Enter choice: ").lower()
    if key == 's':
        send_sos_alert()
    elif key == 'q':
        print("Exiting.")
        break

