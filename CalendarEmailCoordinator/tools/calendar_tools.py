from googleapiclient.discovery import build
from ..auth import get_unified_credentials

def get_calendar_client():
    creds = get_unified_credentials()
    return build("calendar", "v3", credentials=creds)

def create_event(event_summary: str, start_time_iso: str, end_time_iso: str, attendees_emails: list[str] = None):
    """
    Creates a calendar event.
    Args:
        event_summary: Title (e.g. 'Project Meeting')
        start_time_iso: ISO String (e.g. '2026-01-14T15:00:00')
        end_time_iso: ISO String (e.g. '2026-01-14T16:00:00')
    """
    client = get_calendar_client()
    
    event_body = {
        'summary': event_summary,
        'start': {'dateTime': start_time_iso, 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_time_iso, 'timeZone': 'Asia/Kolkata'},
    }
    
    if attendees_emails:
        event_body['attendees'] = [{'email': email} for email in attendees_emails]

    event = client.events().insert(calendarId='primary', body=event_body).execute()
    return f"Event created: {event.get('htmlLink')}"