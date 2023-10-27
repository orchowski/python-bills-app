from functools import reduce
from typing import Set

import infrastructure.logger as logger
from model.commons.aggregate_root import DomainEvent
from model.commons.result import Result, Success, Fail
from model.payments.accounting_document import AccountingDocument, Invoice
from model.payments.stores.accounting_documents_store import AccountingDocumentsStore
from model.payments.vo.accounting_document_id import AccountingDocumentId


class AccountingDocumentsRepository(AccountingDocumentsStore):
    __events: Set[DomainEvent] = set()

    def save(self, document: AccountingDocument) -> Result:
        try:
            super(AccountingDocumentsRepository, self).save(document)
            new_events = document.extract_events_with_state_clearing()
            if len(set(new_events).difference(self.__events)) != len(new_events):
                return Fail("duplicated event for aggregate occured, transaction failed")
            self.__events.update(new_events)
            self.publish_all(new_events)
        except Exception as e:
            logger.error('Test accounting_document repo saving error %s', e)
            return Fail(e)
        return Success()

    def get_by(self, accounting_document_id: AccountingDocumentId) -> AccountingDocument:
        super(AccountingDocumentsRepository, self).get_by(accounting_document_id)
        aggregate_events = list(
            filter(lambda event: event.aggregate_id == accounting_document_id, self.__events))
        return reduce(lambda demand, event: event.apply(demand),
                      sorted(aggregate_events,
                             key=lambda elem: elem.aggregate_version
                             ),
                      AccountingDocument.shell())

    def get_invoice_by(self, accounting_document_id: AccountingDocumentId) -> Invoice:
        super(AccountingDocumentsRepository, self).get_by(accounting_document_id)
        aggregate_events = list(
            filter(lambda event: event.aggregate_id == accounting_document_id, self.__events))
        result = reduce(lambda demand, event: event.apply(demand),
                        sorted(aggregate_events,
                               key=lambda elem: elem.aggregate_version
                               ),
                        AccountingDocument.shell())
        if isinstance(result, Invoice):
            return result
        raise ValueError(f"invoice {accounting_document_id} not found")
