import base64
from email.message import EmailMessage
from googleapiclient.discovery import build

from tools.auth_manager import get_credentials


def send_email(draft):
    """
    Sends a real email using Gmail API.
    """

    # Get OAuth credentials
    creds = get_credentials()

    # Build Gmail service
    service = build("gmail", "v1", credentials=creds)

    # Create email message
    message = EmailMessage()
    message.set_content(draft["body"])
    message["To"] = draft["to"]
    message["From"] = "me"
    message["Subject"] = draft["subject"]

    # Encode message
    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    send_body = {
        "raw": encoded_message
    }

    # Send email
    service.users().messages().send(
        userId="me",
        body=send_body
    ).execute()

    print(" EMAIL SENT SUCCESSFULLY")
