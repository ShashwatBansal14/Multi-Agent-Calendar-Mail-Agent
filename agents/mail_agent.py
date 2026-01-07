class MailAgent:
    def create_draft(self, user_input, selected_files=None):
        """
        Creates an email draft.
        Includes attached Google Drive files if any.
        """

        text = user_input.lower()

        if "meeting" in text:
            subject = "Meeting Request"
        elif "update" in text:
            subject = "Project Update"
        else:
            subject = "Regarding Your Request"

        # Build attachment text
        attachment_text = ""
        if selected_files:
            attachment_names = ", ".join(
                [f["name"] for f in selected_files]
            )
            attachment_text = f"\n\nAttachments:\n{attachment_names}"

        body = (
            f"Hello,\n\n"
            f"This email was created based on your request:\n"
            f"'{user_input}'"
            f"{attachment_text}\n\n"
            f"Regards,\n"
            f"Your Assistant"
        )

        return {
            "to": "example@gmail.com",
            "subject": subject,
            "body": body
        }
