from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

from model.commons.vo.money import Money
from model.commons.vo.user_id import UserId
from model.payments.vo.invoice_number import InvoiceNumber


@dataclass(frozen=True)
class InvoiceData:
    invoice_number: InvoiceNumber
    issued_on: date
    paid_off: bool
    deadline: date
    issuer: Optional[InvoiceIssuer] = None
    originator: Optional[UserId] = None
    tax_money: Optional[Money] = None

    @classmethod
    def init(cls,
             invoice_number: InvoiceNumber,
             issued_on: date,
             paid_off: bool,
             deadline: date = None,
             issuer: Optional[InvoiceIssuer] = None,
             originator: Optional[UserId] = None,
             tax_money: Optional[Money] = None,
             ) -> InvoiceData:
        return cls(
            invoice_number, issued_on,
            paid_off,
            (deadline if deadline is not None else issued_on + timedelta(days=14)),
            issuer,
            originator,
            tax_money
        )


@dataclass(frozen=True)
class InvoiceIssuer:
    id: str
    name: str
