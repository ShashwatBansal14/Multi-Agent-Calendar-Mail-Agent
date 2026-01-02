def create_session():
    """
    Creates a fresh session state for the user.
    This session lives only during runtime (no DB).
    """

    return {
        # Raw user input
        "user_input": None,

        # Intent related
        "intent": None,

        # Email related
        "email_draft": None,
        "email_confirmed": False,
        "email_sent": False,

        # Calendar related
        "calendar_event": None,

        # Google Drive related
        "drive_files": [],
        "selected_files": [],

        # Debug / trace
        "agent_trace": []
    }
