from dataclasses import dataclass
from typing import Optional

from model.commons.vo.correlation_id import CorrelationId
from model.commons.vo.money import Money
from model.payments.vo.invoice_data import InvoiceData


@dataclass(frozen=True)
class AddInvoiceCommand:
    wallet: CorrelationId
    money_gross: Money
    document_resource_id: Optional[CorrelationId]
    invoice_data: InvoiceData
