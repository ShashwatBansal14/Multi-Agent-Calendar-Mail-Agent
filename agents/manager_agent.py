from agents.intent_router_agent import IntentRouterAgent


class ManagerAgent:
    def __init__(self, session):
        """
        Manager Agent controls the flow of the system.
        It receives the shared session memory.
        """
        self.session = session
        self.intent_router = IntentRouterAgent()

    def handle_input(self, user_input):
        # Store input
        self.session["user_input"] = user_input

        # Detect intent
        intent = self.intent_router.classify_intent(user_input)
        self.session["intent"] = intent

        # Log decision
        self.session["agent_trace"].append(f"Intent classified as: {intent}")
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
