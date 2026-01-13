import os
import asyncio
import base64
from datetime import datetime
import pytz
from email.message import EmailMessage
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.auth.transport.requests import Request
from google.adk.sessions import InMemorySessionService

import os
import asyncio
import base64
import mimetypes
from datetime import datetime
import pytz
from email.message import EmailMessage
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.auth.transport.requests import Request

load_dotenv()
oauth_token_cache = {}
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_gmail_credentials_interactive():
    creds = oauth_token_cache.get("gmail")
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        oauth_token_cache["gmail"] = creds
        return creds

    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://127.0.0.1:8000/dev-ui/"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
    )
    creds = flow.run_local_server(prompt='consent')
    oauth_token_cache["gmail"] = creds
    return creds

def get_gmail_client():
    creds = get_gmail_credentials_interactive()
    return build("gmail", "v1", credentials=creds)

def get_current_user_email_id():
    client = get_gmail_client()
    profile = client.users().getProfile(userId='me').execute()
    return profile.get("emailAddress", "")

# async def send_email(sender_id: str, recipient_id: str, subject: str, message: str) -> dict:
#     client = get_gmail_client()
#     message_obj = EmailMessage()
#     message_obj.set_content(message)
#     message_obj['To'] = recipient_id
#     message_obj['From'] = sender_id
#     message_obj['Subject'] = subject
#     encoded_message = base64.urlsafe_b64encode(message_obj.as_bytes()).decode()
#     create_message = {'raw': encoded_message}
#     send_message = await asyncio.to_thread(
#         client.users().messages().send(userId="me", body=create_message).execute
#     )
#     return {"status": "success", "message_id": send_message["id"]}

async def send_email(sender_id: str, recipient_id: str, subject: str, message: str, attachment_paths: list[str] = None) -> dict:
    """Sends an email, optionally with attachments (list of file paths)."""
    client = get_gmail_client()
    message_obj = EmailMessage()
    message_obj.set_content(message)
    message_obj['To'] = recipient_id
    message_obj['From'] = sender_id
    message_obj['Subject'] = subject

    # Handle Attachments
    if attachment_paths:
        for path in attachment_paths:
            # clean path string if LLM adds quotes
            path = path.strip("'").strip('"') 
            if os.path.exists(path):
                ctype, encoding = mimetypes.guess_type(path)
                if ctype is None or encoding is not None:
                    # No guess could be made, or the file is encoded (compressed), so
                    # use a generic bag-of-bits type.
                    ctype = 'application/octet-stream'
                
                maintype, subtype = ctype.split('/', 1)
                
                with open(path, 'rb') as f:
                    file_data = f.read()
                    message_obj.add_attachment(
                        file_data,
                        maintype=maintype,
                        subtype=subtype,
                        filename=os.path.basename(path)
                    )
            else:
                print(f"Warning: Attachment path not found: {path}")

    encoded_message = base64.urlsafe_b64encode(message_obj.as_bytes()).decode()
    create_message = {'raw': encoded_message}
    send_message = await asyncio.to_thread(
        client.users().messages().send(userId="me", body=create_message).execute
    )
    return {"status": "success", "message_id": send_message["id"]}
def get_current_datetime():
    """Get current datetime in IST for context."""
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S %Z')

email_subagent = LlmAgent(
    model='gemini-2.0-flash',
    name='EmailAgent',
    instruction="""You are an email assistant with access to send emails using Gmail API.
    You can send Gmail emails for the authenticated user.

    IMPORTANT: Current date and IST time is: {get_current_datetime()}
    Use this as reference for all relative time expressions (today, tomorrow, etc.)

    You are EmailAgent, a conversational assistant empowered to manage the authenticated user's Gmail mailbox using the "gmail.modify" scope.
    Also you have access to the user's email address via "userinfo.email" scope and other profile information via "userinfo.profile" and "openid" scopes.
    Your capabilities include:
    - Retrieving the user's primary email address.
    - Listing unread or all emails with relevant metadata.
    - Reading full email content, including subject, sender, recipient, date, and plain text body.
    - Sending emails by composing base64url encoded RFC 2822 compliant messages.
    - Deleting emails by moving them to trash.
    - Providing current date and time in IST timezone for context-aware replies.

    For every user request:
    - Determine the appropriate Gmail operation to perform.
    - Execute the action via the provided tool functions.
    - Return a clear, concise summary confirming the success or detailed results of the operation.

    For email sending:
    - Encode emails correctly with base64url encoding without padding.
    - Set the "From" address as the authenticated user's verified email.
    - Include recipients, subject, and body as specified in request.

    Always ensure your replies are direct, accurate, and concise.

    If the EmailAgent is called after CalendarAgent to send meeting invitations, use the event details provided by the output key "event_summary" from CalendarAgent to compose the email content.

    Delegate tasks accordingly based on user requests and ensure smooth coordination between CalendarAgent and EmailAgent.
    Also after completion of the task provided by the user delegate back to the main root agent(CalendarEmailCoordinator).
    """,
    tools=[
        get_current_user_email_id, send_email, get_current_datetime, get_gmail_client
    ],
    output_key="email_summary"
)