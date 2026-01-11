from agents.intent_router_agent import IntentRouterAgent
from agents.mail_agent import MailAgent
from agents.calendar_agent import CalendarAgent

from tools.email_tool import send_email
from tools.calendar_tool import create_calendar_event
from tools.gdrive_tool import list_files


class ManagerAgent:
    """
    Manager Agent orchestrates the full workflow.
    It is the ONLY component that:
    - talks to the user
    - decides which agent/tool to call
    - controls sequencing and safety
    """

    def __init__(self, session):
        self.session = session
        self.intent_router = IntentRouterAgent()
        self.mail_agent = MailAgent()
        self.calendar_agent = CalendarAgent()

    def handle_input(self, user_input):
        """
        Main decision pipeline.
        """

        # ==============================
        # 1. HUMAN-IN-THE-LOOP CHECK
        # ==============================
        if self.session["awaiting_email_confirmation"]:

            if user_input.lower() == "yes":
                # Send real email
                send_email(self.session["email_draft"])

                self.session["email_sent"] = True
                self.session["awaiting_email_confirmation"] = False
                self.session["agent_trace"].append("Email sent successfully")

                # Prepare calendar event data
                event_data = self.calendar_agent.create_event_data(
                    self.session["user_input"]
                )

                # Create real calendar event
                calendar_event = create_calendar_event(event_data)

                self.session["calendar_event"] = calendar_event
                self.session["agent_trace"].append("Calendar event created")

                return (
                    "Email has been sent successfully.\n"
                    "Calendar event has been created."
                )

            elif user_input.lower() == "no":
                self.session["email_draft"] = None
                self.session["awaiting_email_confirmation"] = False
                self.session["agent_trace"].append("Email draft rejected")

                return "Okay, I have discarded the email draft."

            else:
                return "Please reply with 'yes' or 'no'."

        # ==============================
        # 2. GOOGLE DRIVE FILE SELECTION
        # ==============================
        if self.session["drive_files"] and user_input.isdigit():
            selected_file = next(
                (f for f in self.session["drive_files"] if f["id"] == user_input),
                None
            )

            if selected_file:
                self.session["selected_files"].append(selected_file)
                self.session["drive_files"] = []
                self.session["agent_trace"].append(
                    f"Drive file selected: {selected_file['name']}"
                )

                return (
                    f"File '{selected_file['name']}' attached successfully.\n"
                    "You can now send the email."
                )

        # ==============================
        # 3. NORMAL USER INPUT FLOW
        # ==============================
        self.session["user_input"] = user_input

        intent = self.intent_router.classify_intent(user_input)
        self.session["intent"] = intent
        self.session["agent_trace"].append(f"Intent classified as: {intent}")

        # ==============================
        # 4. UNSUPPORTED INTENT
        # ==============================
        if intent == "unsupported":
            return (
                "I can't help with that directly. "
                "I can help you send emails or manage calendar events."
            )

        # ==============================
        # 5. AMBIGUOUS INTENT
        # ==============================
        if intent == "ambiguous":
            return "Could you please provide more details?"

        # ==============================
        # 6. ACTIONABLE INTENT
        # ==============================
        if intent == "actionable":

            # ---- Google Drive attachment flow ----
            if "attach" in user_input.lower() or "file" in user_input.lower():
                files = list_files()
                self.session["drive_files"] = files
                self.session["agent_trace"].append("Drive files listed")

                file_list = "\n".join(
                    [f"{f['id']}. {f['name']}" for f in files]
                )

                return (
                    "I found these files in your Google Drive:\n"
                    f"{file_list}\n\n"
                    "Please enter the file number to attach."
                )

            # ---- Create email draft ----
            draft = self.mail_agent.create_draft(
                user_input,
                self.session["selected_files"]
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
