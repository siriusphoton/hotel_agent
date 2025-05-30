# HomeStay ADK Agent with FastAPI Frontend

This project demonstrates a HomeStay booking agent built with the Google Agent Development Kit (ADK) and served via a FastAPI backend, with a simple HTML/JavaScript streaming chat interface.

## Project Structure

-   `main.py`: FastAPI application that serves the ADK agent.
-   `homestayagent/`: Directory containing the HomeStay ADK agent logic.
    -   `agent.py`: Defines the main `HomeStayAgent`.
    -   `*.tool.py`: Contains various tools used by the agent (availability, booking, user management).
    -   `hotel.db`: SQLite database for homestay information.
    -   `prompts.py`: Contains prompts for the agent.
-   `static/`: Directory containing the frontend.
    -   `index.html`: The HTML/JavaScript chat interface.
-   `.env`: Configuration file for API keys. (Needs to be created by the user)
-   `google_adk_agent/`: (This directory contains a simpler, unused agent created during initial exploration and can be ignored or removed).

## Setup Instructions

### 1. Create a Python Virtual Environment

It's highly recommended to use a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

Install the necessary Python packages:

```bash
pip install google-adk fastapi uvicorn prettytable async_generator
```

### 3. Set Up API Key

You need a Gemini API key to run the agent.

1.  Create a file named `.env` in the root directory of this project.
2.  Add your API key to the `.env` file in the following format:

    ```env
    GOOGLE_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    # If using Google AI Studio keys (not Vertex AI):
    GOOGLE_GENAI_USE_VERTEXAI=FALSE
    # If using Vertex AI, set GOOGLE_GENAI_USE_VERTEXAI=TRUE
    # and ensure your gcloud CLI is configured for the correct project.
    # GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    # GOOGLE_CLOUD_LOCATION="your-gcp-location"
    ```
    Replace `"YOUR_GEMINI_API_KEY_HERE"` with your actual API key.

### 4. Database

The `HomeStayAgent` uses an SQLite database (`homestayagent/hotel.db`). This file is included in the repository.

## Running the Application

### 1. Start the FastAPI Backend

Navigate to the root directory of the project in your terminal and run:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
This will start the FastAPI server. You should see output indicating the server is running, and it will mention that it's using the `HomeStayAgent`.

### 2. Open the Frontend Chat Interface

Open your web browser and navigate to:

[http://localhost:8000/static/index.html](http://localhost:8000/static/index.html)

Alternatively, depending on your setup or if you choose to serve static files differently with FastAPI, you might just open the `static/index.html` file directly in your browser if the FastAPI app is configured to allow requests from `file://` origins (requires CORS configuration, which is not currently set up in `main.py` for direct file opening). For the most reliable experience, access it via the path served by Uvicorn if static file serving is correctly configured in `main.py`.

*(Note: The current `main.py` does not explicitly configure static file serving. For the above URL to work directly, FastAPI would need to be configured to serve the `static` directory. If not, you'd open the `static/index.html` file directly from your filesystem while the backend is running, and ensure your browser allows requests from `file://` to `localhost:8000` or handle potential CORS issues if they arise.)*

You can now chat with the HomeStay agent!

## How it Works

-   The `HomeStayAgent` (`homestayagent/agent.py`) defines the core logic and tools for handling user queries related to bookings and availability.
-   The FastAPI application (`main.py`) uses the ADK's `InMemoryRunner` to execute the agent and streams its responses.
-   The `static/index.html` frontend sends user messages to the FastAPI backend and displays the streamed responses in real-time.
