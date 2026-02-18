from google.adk.agents import Agent,LlmAgent
from .prompts import (coordinator_instructions)
from .availability_fetcher_tool import availability_fetcher
from .booking_tool import booking
from datetime import date
from google.adk.tools import FunctionTool,ToolContext
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import load_artifacts
from google.adk.tools.agent_tool import AgentTool
from .get_user import add_or_get_guest
date_today = date.today()
availability_fetcher_tool = FunctionTool(func=availability_fetcher)
booking_tool = FunctionTool(func=booking)
add_or_get_guest_tool = FunctionTool(func=add_or_get_guest)
root_agent = LlmAgent(
    name='HomeStayAgent',
    model='gemini-2.0-flash',
    description='A helpful assistant for user questions.',
    instruction=coordinator_instructions,
    global_instruction=(
        f"""Todays date: {date_today}"""
    ),
    tools=[availability_fetcher_tool, booking_tool, add_or_get_guest_tool]
)
