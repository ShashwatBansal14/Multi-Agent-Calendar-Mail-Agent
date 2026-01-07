class CalendarAgent:
    def create_event(self, user_input, selected_files=None):
        """
        Creates a calendar event.
        Includes attached file references if any.
        """

        attachment_text = ""
        if selected_files:
            attachment_names = ", ".join(
                [f["name"] for f in selected_files]
            )
            attachment_text = f"Attachments: {attachment_names}"

        return {
            "title": "Meeting",
            "date": "Tomorrow",
            "time": "11:00 AM",
            "description": (
                f"Event created based on: '{user_input}'. "
                f"{attachment_text}"
            )
        }
