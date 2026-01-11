class MailAgent:
    """
    MailAgent is responsible ONLY for creating email drafts.
    It never sends emails.
    """

    def create_draft(self, user_input, selected_files=None):
        """
        Creates an email draft based on user input.
        Adds Google Drive file links if files are attached.
        """

        # Normalize text for simple rule-based intent
        text = user_input.lower()

        # Simple subject selection
        if "meeting" in text:
            subject = "Meeting Request"
        elif "update" in text:
            subject = "Project Update"
        else:
            subject = "Regarding Your Request"

        # Build email body
        body = (
            "Hello,\n\n"
            "This email was created based on your request:\n"
            f"\"{user_input}\"\n"
        )

        # Add Drive attachments (as links)
        if selected_files:
            body += "\nAttached files:\n"
            for file in selected_files:
                body += f"- {file['name']}: {file['link']}\n"

        body += (
            "\nRegards,\n"
            "Your Assistant"
        )

        return {
            "to": "shashwatbansal1414@gmail.com",
            "subject": subject,
            "body": body
        }
