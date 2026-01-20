from google.adk.agents import LlmAgent
from google.adk.tools import transfer_to_agent
from ..utils import get_current_datetime
from ..tools.mail_tools import send_email, get_current_user_email_id
from ..tools.drive_tools import search_pdfs, download_pdf_to_temp

email_subagent = LlmAgent(
    model='gemini-2.0-flash',
    name='EmailAgent',
    instruction="""You are the Email Specialist.
    
    Current date and time is: {get_current_datetime()}

    Your job is to draft and send professional emails. You can also attach PDF files from Google Drive if requested.

    WORKFLOW SCENARIOS:

    1. Scenario: EMAIL WITH ATTACHMENT ("Send resume to Bob", "Attach the report")
       - First, use `search_pdfs` to find the file the user mentioned.
       - If you find multiple files, ask the user to clarify which one to use.
       - Once confirmed, use `download_pdf_to_temp` to get the file path.
       - Only after you have the file path, proceed to draft the email.

    2. Scenario: STANDARD EMAIL ("Email Bob about the meeting")
       - Draft the email immediately using the user's instructions.
       - Fix any typos and ensure the tone is professional and polite.

    DRAFTING & SENDING RULES:
    - Always show the draft to the user first.
    - DO not print any internal function name.
    - Ask "Here is the draft. Shall I send it?"
    - STOP. Do not call the send tool yet. Wait for the user to say "Yes".

    COMPLETION PROTOCOL:
    - If the user says "Yes", call `send_email`.
    - Once the email is sent successfully, say "Email sent successfully."
    - Finally, call the `transfer_to_agent` tool to send the user back to the 'CalendarEmailCoordinator'.
    """,
    tools=[
        get_current_user_email_id, 
        send_email, 
        get_current_datetime,
        search_pdfs,
        download_pdf_to_temp,
        transfer_to_agent
    ],
    output_key="email_summary"
)