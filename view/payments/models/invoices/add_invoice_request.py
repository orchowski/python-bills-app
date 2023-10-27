from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, condecimal, constr, validator


class InvoiceIssuer(BaseModel):
    id: constr(min_length=5)
    name: constr(min_length=5)


class AddInvoiceRequest(BaseModel):
    money_gross: condecimal(gt=0)
    unit: constr(strip_whitespace=True, min_length=3)
    invoice_number: constr(strip_whitespace=True, min_length=5)
    issued_on: date
    paid_off: bool
    deadline: Optional[date]
    issuer: Optional[InvoiceIssuer]
    originator: Optional[str]
    tax_money: Optional[Decimal]
    document_resource: Optional[UUID]

    @validator("issued_on", pre=True)
    def parse_issued_on(cls, value):
        return date.fromisoformat(value)

    @validator("deadline", pre=True)
    def parse_deadline(cls, value):
        return date.fromisoformat(value) if value else None