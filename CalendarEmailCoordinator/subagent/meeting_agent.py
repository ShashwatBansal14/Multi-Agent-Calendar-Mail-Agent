from google.adk.agents import SequentialAgent
from .mail_agent import email_subagent
from .calendar_agent import calendar_subagent

# Create independent copies so they don't conflict with the Manager
email_chain_copy = email_subagent.model_copy()
calendar_chain_copy = calendar_subagent.model_copy()

meeting_agent = SequentialAgent(
    name="MeetingAgent",
    description="Use this for requests that involve BOTH sending an email invitation AND booking a calendar meeting.",
    sub_agents=[calendar_chain_copy, email_chain_copy]
)