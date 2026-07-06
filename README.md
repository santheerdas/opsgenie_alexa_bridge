# opsgenie_alexa_bridge
Notification sending from opsgenie to alexa using python script as a bridge


1. Set Up an App Password (If using Gmail/Microsoft 365)

Modern email providers block direct login via regular passwords.

    If using Gmail, ensure 2-Step Verification is turned on, go to your Google Account security settings, and generate an App Password. Use that 16-character string as your password instead of your primary login.

2. Run Locally or on a Server

You can update your variables and run the script as a background daemon:
Bash

EMAIL_USER="your.email@gmail.com"
EMAIL_PASS="abcd efgh ijkl mnop"
ALEXA_ACCESS_CODE="amzn1.ask.account.XYZ..."
IMAP_SERVER="imap.gmail.com"

python opsgenie_alexa_bridge.py

####Documentation is in progress####
