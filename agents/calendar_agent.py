from datetime import datetime, timedelta


class CalendarAgent:
    """
    Prepares calendar event data.
    """

    def create_event_data(self, user_input):
        # For now, keep it simple and fixed
        start_time = datetime.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        return {
            "title": "Meeting Scheduled via Assistant",
            "description": f"Meeting created based on request: {user_input}",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "attendees": []  # you can add emails later
        }
