class ManagerAgent:
    def __init__(self, session):
        """
        Manager Agent controls the flow of the system.
        It receives the shared session memory.
        """
        self.session = session

    def handle_input(self, user_input):
        """
        Handles user input and updates session memory.
        """

        # Store latest user input
        self.session["user_input"] = user_input

        # Log action
        self.session["agent_trace"].append(f"ManagerAgent received input: {user_input}")

        # Basic response flow (temporary)
        response = f"You said: '{user_input}'. I have stored this in session."

        return response
