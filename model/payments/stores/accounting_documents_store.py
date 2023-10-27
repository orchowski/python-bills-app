from abc import abstractmethod

from model.commons.aggregate_store import AggregateStore
from model.commons.result import Result, Success
from model.payments.accounting_document import AccountingDocument, AccountingDocumentId, Invoice


class AccountingDocumentsStore(AggregateStore):

    @abstractmethod
    def save(self, document: AccountingDocument) -> Result:
        super().save(document)
        if not isinstance(document, AccountingDocument):
            raise TypeError("document should be type of AccountingDocument")
        return Success()

    @abstractmethod
    def get_by(self, document_id: AccountingDocumentId) -> AccountingDocument:
        if not isinstance(document_id, AccountingDocumentId):
            raise TypeError("document_id should be type of AccountingDocumentId")
        pass

    @abstractmethod
    def get_invoice_by(self, document_id: AccountingDocumentId) -> Invoice:
        if not isinstance(document_id, AccountingDocumentId):
            raise TypeError("document_id should be type of AccountingDocumentId")
        pass
