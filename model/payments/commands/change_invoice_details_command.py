from dataclasses import dataclass

from model.payments.vo.accounting_document_id import AccountingDocumentId
from model.payments.vo.invoice_data import InvoiceData


@dataclass(frozen=True)
class ChangeInvoiceDetailsCommand:
    invoice_id: AccountingDocumentId
    invoice_data: InvoiceData
