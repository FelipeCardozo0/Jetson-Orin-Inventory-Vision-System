import os
import smtplib
import ssl
import logging
from email.message import EmailMessage
from datetime import datetime

# --- 1. Persistent Logging Setup ---
# Configure logging to write to a file with timestamps.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("inventory_events.log"),
        logging.StreamHandler() # Also print logs to console
    ]
)

# --- Configuration from environment variables ---
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
NOTIFY_FROM = os.getenv("NOTIFY_FROM", SMTP_USER)
NOTIFY_TO = os.getenv("NOTIFY_TO")

# --- 2. Advanced State Management ---
# This dictionary will track the current state of each item ('OK' or 'LOW_STOCK')
# to prevent duplicate notifications.
item_states = {}

# --- 3. Support for Multiple Notification Channels (Modular Design) ---

def send_email(subject, body, attachment_path=None):
    """Sends an email notification."""
    if not all([SMTP_USER, SMTP_PASS, NOTIFY_TO]):
        logging.warning("Email credentials (SMTP_USER, SMTP_PASS, NOTIFY_TO) not set. Skipping email.")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = NOTIFY_FROM
    msg["To"] = NOTIFY_TO
    msg.set_content(body)

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            data = f.read()
            msg.add_attachment(data, maintype="image", subtype="jpeg", filename=os.path.basename(attachment_path))
    
    ctx = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx) as s:
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
            logging.info(f"Email alert '{subject}' sent successfully to {NOTIFY_TO}")
            return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

def send_slack_message(subject, body):
    """Placeholder for a future Slack integration."""
    logging.info(f"--- SLACK PLACEHOLDER ---\nSubject: {subject}\nBody: {body}\n-------------------------")
    # In a real scenario, you would add your Slack API integration code here.
    return True

def send_notification(subject, body, attachment_path=None, channels=['email']):
    """
    General notification function to dispatch alerts to specified channels.
    """
    for channel in channels:
        if channel == 'email':
            send_email(subject, body, attachment_path)
        elif channel == 'slack':
            send_slack_message(subject, body)
        else:
            logging.warning(f"Unknown notification channel: {channel}")

# --- Main Notification Logic with State Change Detection ---

def check_inventory_state(counts, thresholds, snapshot_path=None):
    """
    Checks item counts against thresholds and sends notifications only when
    the state changes from 'OK' to 'LOW_STOCK' or vice-versa.
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for item, count in counts.items():
        threshold = thresholds.get(item, 0)
        previous_state = item_states.get(item, 'OK')
        current_state = 'LOW_STOCK' if count < threshold else 'OK'

        if current_state != previous_state:
            # State has changed, send a notification
            if current_state == 'LOW_STOCK':
                subject = f"Inventory Alert: {item} is low"
                body = (f"Low stock detected for item: {item}\n\n"
                        f"Time: {ts}\n"
                        f"Current Count: {count}\n"
                        f"Threshold: {threshold}")
                logging.warning(f"LOW STOCK DETECTED for {item}. Count: {count}, Threshold: {threshold}")
                send_notification(subject, body, attachment_path=snapshot_path)

            elif current_state == 'OK':
                subject = f"Inventory Update: {item} has been restocked"
                body = (f"Item has been restocked: {item}\n\n"
                        f"Time: {ts}\n"
                        f"Current Count: {count}\n"
                        f"Threshold: {threshold}")
                logging.info(f"RESTOCKED: {item}. Count: {count}, Threshold: {threshold}")
                send_notification(subject, body, attachment_path=snapshot_path)

            # Update the state for the item
            item_states[item] = current_state

    return item_states

