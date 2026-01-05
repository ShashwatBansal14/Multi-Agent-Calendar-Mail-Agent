from agents.intent_router_agent import IntentRouterAgent
from agents.mail_agent import MailAgent
from tools.email_tool import send_email



class ManagerAgent:
    def __init__(self, session):
        """
        Manager Agent controls the flow of the system.
        It receives the shared session memory.
        """
        self.session = session
        self.intent_router = IntentRouterAgent()
        self.mail_agent=MailAgent()

    def handle_input(self, user_input):
        if self.session["awaiting_email_confirmation"]:
            if user_input.lower() == "yes":
                # Send email
                send_email(self.session["email_draft"])

                # Update session
                self.session["email_confirmed"] = True
                self.session["email_sent"] = True
                self.session["awaiting_email_confirmation"] = False

                self.session["agent_trace"].append(
                    "Email sent successfully"
                )

                return "Email has been sent successfully."

            elif user_input.lower() == "no":
                self.session["email_draft"] = None
                self.session["awaiting_email_confirmation"] = False

                self.session["agent_trace"].append(
                    "User rejected email draft"
                )

                return "Okay, I have discarded the email draft."

            else:
                return "Please reply with 'yes' or 'no'."

        # Store input
        self.session["user_input"] = user_input

        # Detect intent
        intent = self.intent_router.classify_intent(user_input)
        self.session["intent"] = intent

        # Log decision
        self.session["agent_trace"].append(f"Intent classified as: {intent}")
        if intent == "actionable":
            draft = self.mail_agent.create_draft(user_input)
            self.session["email_draft"] = draft
            self.session["awaiting_email_confirmation"] = True


            self.session["agent_trace"].append(
                "MailAgent created email draft"
            )

            return (
                "I have created an email draft:\n"
                f"To: {draft['to']}\n"
                f"Subject: {draft['subject']}\n"
                f"Body: {draft['body']}\n\n"
                "Do you want to send this email? (yes/no)"
            )

        if intent == "unsupported":
            return (
                "I can't help with that directly. "
                "But I can help you send emails or manage calendar events."
            )

        if intent == "ambiguous":
            return (
                "I need more details to proceed. "
                "Could you please clarify your request?"
            )

        return "Got it. I can help with this."
