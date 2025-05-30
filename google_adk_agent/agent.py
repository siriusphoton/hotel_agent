from google.adk.agents import LlmAgent

# Define the root agent for the application
root_agent = LlmAgent(
    name="my_chat_agent",
    model="gemini-1.5-flash-001",  # Using a common Gemini model
    description="A helpful assistant that can engage in conversations.",
    instruction="You are a friendly and helpful conversational assistant. Respond to the user's queries clearly and concisely.",
    # No tools for this simple agent yet
    tools=[]
)

print("Agent definition loaded.")
