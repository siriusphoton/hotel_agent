import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import async_generator

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService, Session
from google.genai.types import Content, Part
from fastapi.staticfiles import StaticFiles

# Import the agent defined in google_adk_agent/agent.py
# Make sure your environment is set up to find this package (e.g., PYTHONPATH)
try:
    from homestayagent.agent import root_agent
except ImportError:
    # This is a fallback for simpler execution environments
    # You might need to adjust PYTHONPATH if running from a different root
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from homestayagent.agent import root_agent


app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize ADK components
# Assuming root_agent is an instance of a class derived from BaseAgent
runner = InMemoryRunner(agent=root_agent, app_name="HomeStayChatApp")

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

async def event_stream_generator(session_id: str, user_message_text: str):
    user_id = "default_user" # In a real app, this would be dynamic

    try:
        # Create or get session
        try:
            session = await runner.session_service.get_session(app_name=runner.app_name, user_id=user_id, session_id=session_id)
            if not session:
                session = await runner.session_service.create_session(app_name=runner.app_name, user_id=user_id, session_id=session_id)
        except Exception as e:
            # Fallback if get_session fails for a new session_id (depends on InMemorySessionService behavior)
            session = await runner.session_service.create_session(app_name=runner.app_name, user_id=user_id, session_id=session_id)

        user_message_content = Content(parts=[Part(text=user_message_text)])

        event_generator = runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=user_message_content
        )

        async for event in event_generator:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        yield f"data: {part.text}\n\n" # SSE format
            # You might want to handle other event types or part types here
            # e.g., function calls, errors, etc.
    except Exception as e:
        print(f"Error during agent processing: {e}")
        yield f"data: Error: {str(e)}\n\n"


@app.post("/chat-stream")
async def chat_stream(request: ChatRequest):
    new_session_id_candidate = request.session_id
    if not new_session_id_candidate:
        temp_session = await runner.session_service.create_session(app_name=runner.app_name, user_id="default_user")
        new_session_id_candidate = temp_session.id
    session_id = new_session_id_candidate

    return StreamingResponse(event_stream_generator(session_id, request.message), media_type="text/event-stream")

if __name__ == "__main__":
    # This is for local testing of the FastAPI app.
    # You would typically run this with: uvicorn main:app --reload
    print("FastAPI backend for ADK Chat Agent")
    print("Run with: uvicorn main:app --reload")
    print("Agent used:", root_agent.name if root_agent else "Agent not loaded")
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    # Commented out uvicorn.run as it might not be suitable for the subtask environment directly.
    # The subtask should focus on file creation and package installation.
