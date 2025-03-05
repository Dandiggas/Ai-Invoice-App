from pydantic import BaseModel, EmailStr
from typing import Optional


class InvoiceDetails(BaseModel):
    invoice_number: Optional[str] = None
    date: str
    client_name: str
    client_email: EmailStr
    service_description: str
    amount: float
