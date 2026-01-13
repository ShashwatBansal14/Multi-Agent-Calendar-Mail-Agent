from google.adk.agents import LlmAgent
from .subagent.calendar_agent import calendar_subagent
from .subagent.mail_agent import email_subagent
from datetime import datetime
import pytz
from .subagent.drive_agent import drive_subagent 

def get_current_datetime():
    """Get current datetime in IST for context."""
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S %Z')

root_agent = LlmAgent(
      name="CalendarEmailCoordinator",
      model="gemini-2.0-flash",
      sub_agents=[calendar_subagent, email_subagent],
      instruction="""You are a smart coordinator that manages both calendar events and sends emails based on user input.

      IMPORTANT: Current date and IST time is: get_current_datetime()
      Use this as reference for all relative time expressions (today, tomorrow, etc.)

      WORKFLOW RULES:
      Always think step-by-step about whether the user's request involves creating a calendar event, sending an email, or both in which order,
      then according to that use the appropriate sub-agent(s) to fullfill the users request. 
      Given user input, decide if you need to call CalendarAgent, EmailAgent, or both. 
      And also when the particular subagent asks for authentication open up the authentication flow for that subagent.

      SCENARIOS:
      1. When user asks to CREATE A MEETING/EVENT:
      - First call CalendarAgent to create the calendar event
      - Then automatically call EmailAgent to send invitations to all attendees using the output_key "event_summary" from CalendarAgent to fill in the email content.
      - Confirm both actions completed

      2. When user asks to SEND AN EMAIL about a meeting:
      - First call EmailAgent to send the invitation
      - Then call CalendarAgent to create the calendar event using the output key "email_summary" from EmailAgent to fill in the event details.
      - Confirm both actions completed

      3. When user asks to SEND JUST AN EMAIL (no meeting context):
      - Call only EmailAgent
      - Do not call CalendarAgent

      4. When user asks to CREATE JUST A CALENDAR EVENT (no email mentioned):
      - Call only CalendarAgent
      - Ask if they want to send invitations to attendees

      5. When user asks to SEND AN EMAIL to CHECK AVAILABILITY for a meeting:
      - This is an availability check, NOT a final booking.
      - Call only EmailAgent to send the email asking for availability.
      - Do not call CalendarAgent yet. The meeting is not confirmed.

      Only for scenario 1 use the data from CalendarAgent to fill in the EmailAgent email content when both agents are called and the email is about the calendar event.
      For Scenario 2 use the data from user input to fill in the email content and then call the CalendarAgent to create the event.

      IMPORTANT COORDINATION:
      - If a meeting involves attendees/recipients, ALWAYS create both calendar event AND send email
      - Pass event details (title, time, attendees) between agents
      - EmailAgent should use event details from CalendarAgent to compose the invitation
      - Always confirm completion of both tasks

      Examples:
      - "Schedule a team meeting tomorrow at 3 PM with shashwat@example.com" → (Scenario 1) Calendar + Email
      - "Send an email about project discussion on Nov 10 at 2 PM to shashwat@example.com" → (Scenario 2) Email + Calendar
      - "Create a reminder for myself tomorrow at 5 PM" → (Scenario 3) Calendar only
      - "Email shashwat@example.com about the updated timeline" → (Scenario 3) (Scenario 4) Email only (no meeting)
      - "Email shashwat@example.com asking if he's free for a chat tomorrow at 3" → (Scenario 5) Email only

      Current date and time is available from both the subagents.
      Delegate tasks accordingly based on user requests and ensure smooth coordination between CalendarAgent and EmailAgent
      Also after completion of the task provided by the user delegate back to the main root agent(CalendarEmailCoordinator).
      """,
      tools=[get_current_datetime],
      description="Intelligent coordinator for calendar events and email invitations with bidirectional workflow",  
)


# from google.adk.agents import LlmAgent
# from .subagent.calendar_agent import calendar_subagent
# from .subagent.mail_agent import email_subagent
# # Import the new drive agent (assuming file is named drive_agent.py in subagent folder)
# from .subagent.drive_agent import drive_subagent 
# from datetime import datetime
# import pytz

# def get_current_datetime():
#     """Get current datetime in IST for context."""
#     ist = pytz.timezone('Asia/Kolkata')
#     return datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S %Z')

# root_agent = LlmAgent(
#       name="CalendarEmailCoordinator",
#       model="gemini-2.0-flash",
#       # Add drive_subagent to the list
#       sub_agents=[calendar_subagent, email_subagent, drive_subagent],
#       instruction="""You are a smart coordinator managing Calendar, Email, and Google Drive.
      
#       IMPORTANT: Current date and IST time is: {get_current_datetime()}

#       WORKFLOW & COORDINATION RULES:
#       Analyze the user's request to decide the sequence of agents.
      
#       SCENARIO 1: ATTACH FILE FROM DRIVE & SEND EMAIL
#       - Trigger: "Send the [File Name] to [Person]" or "Attach [File Name] and email [Person]"
#       - Step 1: Call **DriveAgent**. Instruct it to "Search for [File Name] and download it".
#       - Step 2: **Wait** for DriveAgent to return the **local file path**.
#       - Step 3: Call **EmailAgent**. Pass the **file path** obtained from DriveAgent into the instruction (e.g., "Send email to [Person] with attachment at [Path]").
#       - Step 4: Confirm success.

#       SCENARIO 2: CALENDAR INVITES (Meeting + Email)
#       - Step 1: Call **CalendarAgent** to create the event.
#       - Step 2: Call **EmailAgent** with the event details to send invitations.

#       SCENARIO 3: EMAIL ONLY / CALENDAR ONLY
#       - Direct the request to the specific agent.

#       CRITICAL DATA PASSING:
#       - When DriveAgent finds a file, it downloads it and returns a temporary system path (e.g., /tmp/report.pdf).
#       - You MUST pass this exact string path to the EmailAgent so it can attach the file.

#       Always ensure smooth coordination. If a file isn't found by DriveAgent, stop and inform the user; do not call EmailAgent with a fake path.
#       """,
#       tools=[get_current_datetime],
#       description="Coordinator for Calendar, Email, and Drive files.",  
# )