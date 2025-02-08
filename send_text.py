import smtplib
import os
from rich.console import Console
from datetime import datetime, timedelta
from dateutil.parser import isoparse
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()
console = Console()

# Your T-Mobile email-to-SMS address
TO_SMS = os.getenv("TO_SMS")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_sms_via_email(all_events):
    """
    Sends an event summary via T-Mobile's Email-to-SMS gateway.
    If the message exceeds 160 characters, it splits it into multiple SMSs.

    :param all_events: List of parsed event dictionaries.
    """
    if not all_events:
        print("❌ No events to send.")
        return

    # Filter only today's and tomorrow's events
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    events = []
    for day in all_events:
        if isoparse(day["timestamp"]).date() in [today, tomorrow]:
            events.append(day)

    # Order events by timestamp
    events.sort(key=lambda x: isoparse(x["timestamp"]))

    # Format the full message
    full_message = ""
    for i, day in enumerate(events):
        day_identifier = "today\n" if i == 0 else "tomorrow\n" if i == 1 else None
        full_message += f"{day_identifier}"
        for event in day["events"]:
            title = re.sub(r'[^\w]', '', event["title"])
            location = re.sub(r'\s+', '', event["location"])
            time = '-'.join(re.findall(r'\d+', event["time"]))
            price = re.sub(r'[^\d$]+', '', event["price"])
            full_message += f"{title} {time} {location} {price}\n"

    # Split message into 160-character chunks
    sms_parts = [full_message[i:i+160] for i in range(0, len(full_message), 160)]

    # Send each part as a separate SMS
    for index, part in enumerate(sms_parts):
        subject = f"DC Events ({index + 1}/{len(sms_parts)})"  # Add message count
        message = f"Subject: {subject}\n\n{part}"

        try:
            # Connect to SMTP server
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, TO_SMS, message)
            server.quit()
            print(f"✅ SMS Part {index + 1} sent!")
        except Exception as e:
            raise Exception(f"❌ Error sending SMS via Email: {e}") from e
