class CalendarAgent:
    def create_event(self, user_input):
        """
        Creates a basic calendar event from user input.
        This is mock logic for now.
        """

        event = {
            "title": "Meeting",
            "date": "Tomorrow",
            "time": "11:00 AM",
            "description": f"Event created based on: '{user_input}'"
        }

        return event
