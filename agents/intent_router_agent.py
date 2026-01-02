class IntentRouterAgent:
    def classify_intent(self, user_input):
        """
        Classifies user intent into:
        - actionable
        - ambiguous
        - unsupported
        """

        text = user_input.lower()

        # Unsupported / irrelevant requests
        if "eat" in text or "food" in text:
            return "unsupported"

        # Very generic requests (missing details)
        if text in ["send mail", "send email", "schedule meeting"]:
            return "ambiguous"

        # Otherwise, assume it is actionable for now
        return "actionable"
