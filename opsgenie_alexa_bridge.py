import time
import imaplib
import email
from email.header import decode_header
import requests

# ==========================================
# USER VARIABLES (EDIT THESE BEFORE RUNNING)
# ==========================================
ALEXA_ACCESS_CODE = "YOUR_NOTIFY_ME_ACCESS_CODE"
ALEXA_API_URL = "https://api.notifymyecho.com/v1/NotifyMe"

EMAIL_USER = "your.email@gmail.com"
EMAIL_PASS = "your-16-digit-app-password"

IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

SENDER_FILTER = "noreply@opsgenie.com"
# ==========================================


# --- Configuration & Setup ---
POLL_INTERVAL = 15  # Time in seconds to wait between checking the inbox


def decode_mime_words(s):
    """Safely decode email headers like subjects."""
    if not s:
        return ""
    decoded_words = decode_header(s)
    return "".join(
        word.decode(encoding or "utf-8") if isinstance(word, bytes) else word
        for word, encoding in decoded_words
    )


def send_to_alexa(alert_message):
    """Fires the POST request to the Alexa Notify Me API."""
    payload = {
        "notification": f"Opsgenie Alert: {alert_message}",
        "accessCode": ALEXA_ACCESS_CODE
    }
    
    try:
        response = requests.post(ALEXA_API_URL, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"[+] Successfully sent to Alexa: {alert_message}")
        else:
            print(f"[-] Alexa API rejected request: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"[-] Failed to connect to Alexa API: {e}")


def check_email():
    """Connects to IMAP, searches for unread alerts, and processes them."""
    try:
        # Connect and login
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        # Search for UNREAD emails from the specified sender
        # Format: (FROM "noreply@opsgenie.com" UNSEEN)
        search_criterion = f'(FROM "{SENDER_FILTER}" UNSEEN)'
        status, messages = mail.search(None, search_criterion)

        if status != "OK":
            print("[-] Failed to search email box.")
            return

        message_ids = messages[0].split()
        if not message_ids:
            return  # No new alerts

        print(f"[*] Found {len(message_ids)} new Opsgenie alert email(s). Processing...")

        for msg_id in message_ids:
            # Fetch email headers
            status, msg_data = mail.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = decode_mime_words(msg["Subject"])
                    
                    # Forward the cleaned subject line to Alexa
                    if subject:
                        send_to_alexa(subject)
            
            # Mark the email as read (SEEN) so it isn't processed again next loop
            mail.store(msg_id, "+FLAGS", "\\Seen")

        # Clean up connection
        mail.close()
        mail.logout()

    except imaplib.IMAP4.error as auth_err:
        print(f"[-] IMAP Authentication/Connection failed: {auth_err}")
    except Exception as e:
        print(f"[-] An unexpected error occurred: {e}")


def main():
    print(f"[*] Starting Opsgenie-to-Alexa IMAP Daemon listening to {EMAIL_USER}...")
    print(f"[*] Filtering for sender: {SENDER_FILTER}")
    
    while True:
        check_email()
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()