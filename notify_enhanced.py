#!/usr/bin/env python3
"""
notify_enhanced.py - Enhanced notification module with CSV attachment support

This is an enhanced version of notify.py that adds support for attaching
CSV files (and other file types) to email notifications.

This module can replace the original notify.py or be used alongside it.
"""

import os
import smtplib
import ssl
import logging
from email.message import EmailMessage
from email.mime.text import MimeText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# --- Persistent Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("inventory_events.log"),
        logging.StreamHandler()
    ]
)

# --- Configuration from environment variables ---
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
NOTIFY_FROM = os.getenv("NOTIFY_FROM", SMTP_USER)
NOTIFY_TO = os.getenv("NOTIFY_TO")

# --- State Management ---
item_states = {}


def send_email(subject, body, attachment_path=None):
    """
    Sends an email notification with optional file attachment.
    
    This enhanced version supports multiple file types including CSV, JPEG, PDF, etc.
    
    Args:
        subject (str): Email subject line
        body (str): Email body text
        attachment_path (str): Optional path to file to attach
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if not all([SMTP_USER, SMTP_PASS, NOTIFY_TO]):
        logging.warning("Email credentials (SMTP_USER, SMTP_PASS, NOTIFY_TO) not set. Skipping email.")
        return False

    # Create message
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = NOTIFY_FROM
    msg["To"] = NOTIFY_TO
    
    # Attach body text
    msg.attach(MIMEText(body, 'plain'))

    # Attach file if provided
    if attachment_path and os.path.exists(attachment_path):
        try:
            filename = os.path.basename(attachment_path)
            
            # Determine MIME type based on file extension
            if attachment_path.lower().endswith('.csv'):
                maintype = 'text'
                subtype = 'csv'
            elif attachment_path.lower().endswith(('.jpg', '.jpeg')):
                maintype = 'image'
                subtype = 'jpeg'
            elif attachment_path.lower().endswith('.png'):
                maintype = 'image'
                subtype = 'png'
            elif attachment_path.lower().endswith('.pdf'):
                maintype = 'application'
                subtype = 'pdf'
            else:
                maintype = 'application'
                subtype = 'octet-stream'
            
            # Read and attach file
            with open(attachment_path, 'rb') as f:
                file_data = f.read()
                
                part = MIMEBase(maintype, subtype)
                part.set_payload(file_data)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename= {filename}')
                msg.attach(part)
                
            logging.info(f"Attached file: {filename} ({maintype}/{subtype})")
            
        except Exception as e:
            logging.error(f"Failed to attach file {attachment_path}: {e}")
    
    # Send email
    ctx = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx) as s:
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
            logging.info(f"Email '{subject}' sent successfully to {NOTIFY_TO}")
            return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False


def send_slack_message(subject, body):
    """Placeholder for future Slack integration."""
    logging.info(f"--- SLACK PLACEHOLDER ---\nSubject: {subject}\nBody: {body}\n-------------------------")
    return True


def send_notification(subject, body, attachment_path=None, channels=['email']):
    """
    General notification function to dispatch alerts to specified channels.
    
    Args:
        subject (str): Notification subject
        body (str): Notification body text
        attachment_path (str): Optional file to attach
        channels (list): List of notification channels to use
    """
    for channel in channels:
        if channel == 'email':
            send_email(subject, body, attachment_path)
        elif channel == 'slack':
            send_slack_message(subject, body)
        else:
            logging.warning(f"Unknown notification channel: {channel}")


def check_inventory_state(counts, thresholds, snapshot_path=None):
    """
    Checks item counts against thresholds and sends notifications only when
    the state changes from 'OK' to 'LOW_STOCK' or vice-versa.
    
    Args:
        counts (dict): Current item counts
        thresholds (dict): Threshold values for each item
        snapshot_path (str): Path to image snapshot to attach
    
    Returns:
        dict: Current item states
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

