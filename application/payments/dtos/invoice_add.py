from dataclasses import dataclass
from typing import Optional

from model.commons.vo.correlation_id import CorrelationId
from model.commons.vo.money import Money
from model.payments.vo.invoice_data import InvoiceData


@dataclass(frozen=True)
class InvoiceAddDTO:
    money_gross: Money
    invoice_data: InvoiceData
    document_resource_id: Optional[CorrelationId]
