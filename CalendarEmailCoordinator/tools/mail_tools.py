import os
import base64
import mimetypes
import asyncio
from email.message import EmailMessage
from googleapiclient.discovery import build
# We go up (..) to root to find auth.py
from ..auth import get_unified_credentials

def get_gmail_client():
    creds = get_unified_credentials()
    return build("gmail", "v1", credentials=creds)

def get_current_user_email_id():
    client = get_gmail_client()
    profile = client.users().getProfile(userId='me').execute()
    return profile.get("emailAddress", "")

async def send_email(recipient_id: str, subject: str, message: str, attachment_paths: list[str] = None) -> dict:
    client = get_gmail_client()
    sender_email = get_current_user_email_id()
    
    message_obj = EmailMessage()
    message_obj.set_content(message)
    message_obj['To'] = recipient_id
    message_obj['From'] = sender_email
    message_obj['Subject'] = subject

    if attachment_paths:
        for path in attachment_paths:
            path = path.strip("'").strip('"') 
            if os.path.exists(path):
                ctype, encoding = mimetypes.guess_type(path)
                if ctype is None: ctype = 'application/octet-stream'
                maintype, subtype = ctype.split('/', 1)
                with open(path, 'rb') as f:
                    message_obj.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(path))

    encoded_message = base64.urlsafe_b64encode(message_obj.as_bytes()).decode()
    create_message = {'raw': encoded_message}
    
    send_message = await asyncio.to_thread(
        client.users().messages().send(userId="me", body=create_message).execute
    )
    return {"status": "success", "message_id": send_message["id"]}