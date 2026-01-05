def send_email(email_draft):
    """
    Mock email sending function.
    This simulates sending an email.
    """

    print("\n SENDING EMAIL (MOCK)")
    print(f"To: {email_draft['to']}")
    print(f"Subject: {email_draft['subject']}")
    print(f"Body: {email_draft['body']}")
    print("EMAIL SENT SUCCESSFULLY\n")

    return True
