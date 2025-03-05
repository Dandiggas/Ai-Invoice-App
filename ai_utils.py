import os
from openai import OpenAI

client = OpenAI()
import json
from models import InvoiceDetails
import re  # Needed to clean currency symbols
from datetime import datetime

# Ensure the API key is loaded
openai = os.getenv("OPENAI_API_KEY")


def extract_invoice_details(message):
    """
    Extract invoice details from natural language text using simple pattern matching.
    In a production environment, you would replace this with a more sophisticated
    AI model like OpenAI's GPT or a similar language model.
    """
    # Default values
    invoice_data = {
        "invoice_number": None,
        "date": datetime.now().strftime("%d-%m-%Y"),
        "client_name": "",
        "client_email": "example@example.com",  # Default placeholder
        "service_description": "",
        "amount": 0.0,
    }

    # Extract invoice number
    invoice_match = re.search(
        r"invoice\s*(?:number|#|num)?\s*[:]?\s*([A-Za-z0-9-]+)", message, re.IGNORECASE
    )
    if invoice_match:
        invoice_data["invoice_number"] = invoice_match.group(1)

    # Extract date
    date_match = re.search(
        r"date\s*[:]?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})", message, re.IGNORECASE
    )
    if date_match:
        invoice_data["date"] = date_match.group(1)

    # Extract client name
    client_match = re.search(
        r"client\s*[:]?\s*([A-Za-z\s]+?)(?:\s*email|\s*service|\s*amount|\s*$)",
        message,
        re.IGNORECASE,
    )
    if client_match:
        invoice_data["client_name"] = client_match.group(1).strip()

    # Extract client email
    email_match = re.search(
        r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", message
    )
    if email_match:
        invoice_data["client_email"] = email_match.group(1)

    # Extract service description
    service_match = re.search(
        r"service\s*[:]?\s*([^£$€0-9]+?)(?:\s*amount|\s*£|\s*\$|\s*€|\s*$)",
        message,
        re.IGNORECASE,
    )
    if service_match:
        invoice_data["service_description"] = service_match.group(1).strip()

    # Extract amount
    amount_match = re.search(
        r"(?:amount|cost|price|fee)\s*[:]?\s*[£$€]?\s*(\d+(?:\.\d{1,2})?)",
        message,
        re.IGNORECASE,
    )
    if amount_match:
        invoice_data["amount"] = float(amount_match.group(1))

    return InvoiceDetails(**invoice_data)


def generate_invoice_pdf(invoice_data):
    """
    Generate a PDF invoice using the createpdf module
    """
    from createpdf import createpdf

    # Format data for the createpdf function
    services = [
        {"description": invoice_data.service_description, "price": invoice_data.amount}
    ]
    pdf_name = f"invoice_{invoice_data.client_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"

    # Generate a simple account and client address if not provided
    user_details = "Your Company Name"
    account_details = "Bank: MyBank, Account: 12345678, Sort Code: 12-34-56"
    client_address = "Client's Address"

    # Create the PDF
    pdf_path = createpdf(
        invoice_data.invoice_number or f"INV-{datetime.now().strftime('%Y%m%d')}",
        invoice_data.date,
        user_details,
        account_details,
        invoice_data.client_name,
        client_address,
        services,
        invoice_data.amount,
        pdf_name,
    )

    return pdf_path
