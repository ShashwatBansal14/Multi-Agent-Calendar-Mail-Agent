import os
from datetime import datetime
import pytz
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.adk.agents.llm_agent import LlmAgent
from google.auth.transport.requests import Request
from google.adk.sessions import InMemorySessionService

load_dotenv()
oauth_token_cache = {}

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_credentials_interactive():
    creds = oauth_token_cache.get("calendar")
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        oauth_token_cache["calendar"] = creds
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
    oauth_token_cache["calendar"] = creds
    return creds

def get_calendar_client():
    creds = get_calendar_credentials_interactive()
    return build("calendar", "v3", credentials=creds)

def get_current_datetime():
    """Get current datetime in IST for context."""
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S %Z')

def create_event(calendar_id: str, event_body: dict):
    if not calendar_id:
        calendar_id = "primary"

    if event_body is None:
       
        current_dt_str = get_current_datetime()
        current_date_part = current_dt_str.split(' ')[0]
        ist = pytz.timezone("Asia/Kolkata")

        start_time = time(15, 0)
        end_time = time(15, 30)

        start_dt = datetime.strptime(current_date_part, "%Y-%m-%d").replace(
            hour=start_time.hour, minute=start_time.minute, second=0, microsecond=0)
        end_dt = datetime.strptime(current_date_part, "%Y-%m-%d").replace(
            hour=end_time.hour, minute=end_time.minute, second=0, microsecond=0)

        start_dt_tz = ist.localize(start_dt)
        end_dt_tz = ist.localize(end_dt)

        event_body = {
            'summary': 'Sample Event',
            'start': {'dateTime': start_dt_tz.isoformat(), 'timeZone': 'Asia/Kolkata'},
            'end': {'dateTime': end_dt_tz.isoformat(), 'timeZone': 'Asia/Kolkata'},
        }

    client = get_calendar_client()
    event = client.events().insert(calendarId=calendar_id, body=event_body).execute()
    return event

calendar_subagent = LlmAgent(
    model="gemini-2.0-flash",
    name="CalendarAgent",
    instruction=""""You are CalendarAgent, a conversational assistant managing the authenticated user's Google Calendar via the "calendar" scope.
    You can list calendars, create, retrieve, update, and delete events for the authenticated user using Google Calendar API.
    
    IMPORTANT: Current date and IST time is: get_current_datetime()
    Use this as reference for all relative time expressions (today, tomorrow, etc.)

    YOUR ROLE:
    Create and manage calendar events for meetings, reminders, and appointments.
    Generate event details based on user input, extract details from user input, and format them correctly for Google Calendar API.
    
    Your responsibilities include:
    - Listing user calendars and their metadata.
    - Creating events with detailed date/time, time zone (Asia/Kolkata), attendees, reminders, and location(if available).
    - Retrieving and summarizing event details.
    - Updating existing events with changed information.
    - Deleting events upon request.
    - Providing current IST datetime for context-aware interactions.

    For each user prompt:
    - Parse intent carefully to choose the appropriate calendar operation.
    - When creating events, ensure correct ISO 8601 date-time formatting and timezone usage.
    - When asked, pass event details (title, date/time, attendees) to EmailAgent for sending invitations.
    - Return clear, concise confirmations or data summaries to the user.
    - Respond with user-friendly date/time descriptions in IST.

    If asked for reminders Create/manage events with reminders otherwise ignore reminders.
    Reminders: Use 'popup' or 'email' method with minutes before event (e.g., 30 for 30 minutes).
    Calculate dates and times based on the current date/time provided above.
    Also, if the duration for a meeting is not specified assume a default duration of 30 minutes.

    If the CalendarAgent is called after EmailAgent to send calendar invites, use the email details provided by the output key "email_summary" from EmailAgent to compose the calendar event. Also dont treat the attendees email as the calendar_id rather use the primary calendar for authenticated user.

    Maintain seamless collaboration with EmailAgent for tasks involving meeting invitations or availability requests.
    Also after completion of the task provided by the user delegate back to the main root agent(CalendarEmailCoordinator).
    Always give informative, accurate, and succinct responses suited for a conversational interface.
    
    """,
    tools=[create_event, get_current_datetime],
    output_key="event_summary"
)