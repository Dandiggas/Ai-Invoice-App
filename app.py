from fastapi import FastAPI, Form, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Store chatbot state (for simplicity, using a dictionary instead of a database)
chat_sessions = {}


def get_chat_session(session_id: str):
    """Retrieve or initialize a chat session"""
    if session_id not in chat_sessions:
        chat_sessions[session_id] = {"step": "client_name", "data": {}}
    return chat_sessions[session_id]


@app.get("/", response_class=HTMLResponse)
async def serve_chat_ui(request: Request):
    """Render chatbot UI"""
    return templates.TemplateResponse("chat.html", {"request": request})


@app.post("/chat")
async def chat(request: Request, message: str = Form(...)):
    """Handle chatbot conversation"""
    session_id = request.client.host  # Identify user session by IP (can use UUID)
    chat_session = get_chat_session(session_id)

    step = chat_session["step"]
    data = chat_session["data"]

    response = ""

    if message.lower() in ["exit", "quit"]:
        chat_sessions.pop(session_id, None)
        return {"response": "Chatbot session ended. Refresh the page to restart."}

    if message.lower() == "reset":
        chat_sessions[session_id] = {"step": "client_name", "data": {}}
        return {
            "response": "Session reset. Let's start a new invoice. What's the client’s name?"
        }

    if step == "client_name":
        data["client_name"] = message
        chat_session["step"] = "service_description"
        response = f"Got it! Client name is {message}. What service did you provide?"

    elif step == "service_description":
        data["service_description"] = message
        chat_session["step"] = "price"
        response = f"Service noted: {message}. How much did you charge?"

    elif step == "price":
        try:
            data["price"] = float(message)
            chat_session["step"] = "complete"
            response = (
                f"Price recorded: £{data['price']}. Here's the summary: {data}. "
                "Type 'reset' to start over or 'exit' to quit."
            )
        except ValueError:
            response = "Please enter a valid numeric price."

    return {"response": response}
