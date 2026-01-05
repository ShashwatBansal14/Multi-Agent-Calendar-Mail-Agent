class MailAgent:
    def create_draft(self, user_input):
        """
        Creates a simple email draft from user input.
        Subject is generated dynamically using keywords.
        """

        text = user_input.lower()

        # Simple subject generation 
        if "meeting" in text:
            subject = "Meeting Request"
        elif "follow up" in text or "follow-up" in text:
            subject = "Follow-up Email"
        elif "update" in text:
            subject = "Project Update"
        else:
            subject = "Regarding Your Request"

        draft = {
            "to": "example@gmail.com",
            "subject": subject,
            "body": (
                f"Hello,\n\n"
                f"This email was created based on your request:\n"
                f"'{user_input}'\n\n"
                f"Regards,\n"
                f"Your Assistant"
            )
        }

        return draft
