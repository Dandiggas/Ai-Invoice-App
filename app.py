from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from ai_utils import extract_invoice_details
from models import InvoiceDetails
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

chat_sessions = {}


@app.get("/", response_class=HTMLResponse)
async def serve_chat_ui(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@app.post("/chat")
async def chat(request: Request, message: str = Form(...)):
    session_id = request.client.host
    if session_id not in chat_sessions:
        chat_sessions[session_id] = {"step": "parsing", "data": {}}

    step = chat_sessions[session_id]["step"]
    data = chat_sessions[session_id]["data"]

    if message.lower() in ["exit", "quit"]:
        chat_sessions.pop(session_id, None)
        return {"response": "Chatbot session ended. Refresh the page to restart."}

    if message.lower() == "reset":
        chat_sessions[session_id] = {"step": "parsing", "data": {}}
        return {"response": "Session reset. Please describe the invoice details."}

    if step == "parsing":
        try:
            invoice_data: InvoiceDetails = extract_invoice_details(message)
            data.update(invoice_data.dict())
            chat_sessions[session_id]["step"] = "confirm"
            response = f"""
                Got it! Here's what I extracted:
                - Invoice: {invoice_data.invoice_number or 'Not provided'}
                - Client: {invoice_data.client_name}
                - Email: {invoice_data.client_email}
                - Date: {invoice_data.date}
                - Service: {invoice_data.service_description}
                - Amount: £{invoice_data.amount}
                
                Type 'confirm' to proceed, or 'reset' to start over.
            """
        except Exception as e:
            response = f"Error parsing invoice details: {e}. Try again."

    elif step == "confirm":
        if message.lower() == "confirm":
            response = "Invoice details confirmed. Next step: PDF generation."
            chat_sessions[session_id]["step"] = "pdf"
        else:
            response = "Type 'confirm' to proceed, or 'reset' to start over."

    return {"response": response}
