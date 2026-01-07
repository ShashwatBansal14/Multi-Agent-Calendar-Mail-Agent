from agents.intent_router_agent import IntentRouterAgent
from agents.mail_agent import MailAgent
from agents.calendar_agent import CalendarAgent
from tools.email_tool import send_email
from tools.gdrive_tool import list_files


class ManagerAgent:
    def __init__(self, session):
        """
        Manager Agent controls the full workflow.
        """
        self.session = session
        self.intent_router = IntentRouterAgent()
        self.mail_agent = MailAgent()
        self.calendar_agent = CalendarAgent()

    def handle_input(self, user_input):
        """
        Main decision pipeline.
        Order MATTERS.
        """
        if self.session["awaiting_email_confirmation"]:

            if user_input.lower() == "yes":
                # Send email (mock for now)
                send_email(self.session["email_draft"])

                self.session["email_confirmed"] = True
                self.session["email_sent"] = True
                self.session["awaiting_email_confirmation"] = False

                self.session["agent_trace"].append("Email sent successfully")

                # Create calendar event AFTER email
                event = self.calendar_agent.create_event(
                    self.session["user_input"], self.session["selected_files"]
                )

                self.session["calendar_event"] = event

                self.session["agent_trace"].append("Calendar event created")

                return (
                    " Email has been sent successfully.\n"
                    " Calendar event has been created."
                )

            elif user_input.lower() == "no":
                self.session["email_draft"] = None
                self.session["awaiting_email_confirmation"] = False

                self.session["agent_trace"].append("Email draft rejected")

                return " Email draft discarded."

            else:
                return "Please reply with **yes** or **no**."

        if self.session["drive_files"] and user_input.isdigit():
            selected = next(
                (f for f in self.session["drive_files"] if f["id"] == user_input), None
            )

            if selected:
                self.session["selected_files"].append(selected)
                self.session["drive_files"] = []

                self.session["agent_trace"].append(
                    f"Drive file selected: {selected['name']}"
                )

                return (
                    f" File '{selected['name']}' attached successfully.\n"
                    "You can now send an email or schedule a calendar event."
                )

        self.session["user_input"] = user_input

        intent = self.intent_router.classify_intent(user_input)
        self.session["intent"] = intent

        self.session["agent_trace"].append(f"Intent classified as: {intent}")

        if intent == "unsupported":
            return (
                "I can't help with that directly. "
                "But I can help with emails or calendar events."
            )

        if intent == "ambiguous":
            return "Please provide more details."

        if intent == "actionable":

            #  Google Drive listing request
            if "attach" in user_input.lower() or "file" in user_input.lower():
                files = list_files()
                self.session["drive_files"] = files

                file_list = "\n".join([f"{f['id']}. {f['name']}" for f in files])

                self.session["agent_trace"].append("Drive files listed")

                return (
                    " I found these files in your Google Drive:\n"
                    f"{file_list}\n\n"
                    "Please enter the file number to attach."
                )

            #  Create email draft
            draft = self.mail_agent.create_draft(
                user_input, self.session["selected_files"]
            )

            self.session["email_draft"] = draft
            self.session["awaiting_email_confirmation"] = True

            self.session["agent_trace"].append("Email draft created")

            return (
                "I have created an email draft:\n\n"
                f"To: {draft['to']}\n"
                f"Subject: {draft['subject']}\n"
                f"Body:\n{draft['body']}\n\n"
                "Do you want to send this email? (yes/no)"
            )

        return "I'm not sure how to help with that."
