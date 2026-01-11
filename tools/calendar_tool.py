from googleapiclient.discovery import build
from tools.auth_manager import get_credentials
from datetime import datetime, timedelta


def create_calendar_event(event_data):
    """
    Creates a real Google Calendar event.
    """

    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    event = {
        "summary": event_data["title"],
        "description": event_data["description"],
        "start": {
            "dateTime": event_data["start_time"],
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": event_data["end_time"],
            "timeZone": "Asia/Kolkata",
        },
        "attendees": [
            {"email": email} for email in event_data.get("attendees", [])
        ],
    }

    created_event = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    print("CALENDAR EVENT CREATED")
    print("Event link:", created_event.get("htmlLink"))

    return created_event
