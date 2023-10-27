from dataclasses import dataclass

from model.payments.vo.purpose import PaymentCategory


@dataclass(frozen=True)
class InitInvoicePaymentDTO:
    accounting_document_id: str
    payment_category: PaymentCategory
