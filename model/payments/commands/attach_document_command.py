from dataclasses import dataclass

from model.commons.vo.correlation_id import CorrelationId
from model.payments.vo.accounting_document_id import AccountingDocumentId


@dataclass(frozen=True)
class AttachDocumentCommand:
    document_id: AccountingDocumentId
    document_resource_id: CorrelationId
