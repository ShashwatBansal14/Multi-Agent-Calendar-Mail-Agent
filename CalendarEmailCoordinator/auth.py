import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/drive.readonly",
]

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

_creds = None


def get_unified_credentials():
    global _creds

    #  Use existing session if valid
    if _creds and _creds.valid:
        return _creds

    #  Refresh session if expired
    if _creds and _creds.expired and _creds.refresh_token:
        try:
            _creds.refresh(Request())
            return _creds
        except Exception:
            pass

    #  New Login
    print("Initiating Google Login...")
    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": ["http://localhost:8080/"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
    )

    # FORCE Port 8080
    _creds = flow.run_local_server(port=8080, prompt="consent")
    return _creds
