from __future__ import annotations

from datetime import datetime
from typing import Optional

from model.commons.aggregate_root import AggregateRoot, DomainEvent, EventId
from model.commons.time import current_datetime
from model.commons.vo.correlation_id import CorrelationId
from model.commons.vo.money import Money
from model.payments.vo.accounting_document_id import AccountingDocumentId
from model.payments.vo.invoice_data import InvoiceData


class AccountingDocumentAddedEvent(DomainEvent):
    wallet: CorrelationId
    money_gross: Money
    document_resource_id: Optional[CorrelationId]

    def apply(self, aggregate_root):
        return aggregate_root.apply_document_added(self)

    def __init__(self,
                 event_id: EventId,
                 aggregate_id: AccountingDocumentId,
                 aggregate_version: int,
                 occurrence_date: datetime,
                 money_gross: Money,
                 wallet: CorrelationId,
                 document_resource_id: Optional[CorrelationId]
                 ):
        super().__init__(event_id, aggregate_id, aggregate_version, occurrence_date)
        self.wallet = wallet
        self.money_gross = money_gross
        self.document_resource_id = document_resource_id

    @classmethod
    def create(cls,
               aggregate_id: AccountingDocumentId,
               money_gross: Money,
               wallet: CorrelationId,
               document_resource_id: Optional[CorrelationId]
               ) -> AccountingDocumentAddedEvent:
        return cls(
            event_id=EventId.new(),
            aggregate_id=aggregate_id,
            aggregate_version=1,
            occurrence_date=current_datetime(),
            money_gross=money_gross,
            wallet=wallet,
            document_resource_id=document_resource_id
        )


class InvoiceAddedEvent(DomainEvent):
    invoice_data: InvoiceData

    def __init__(self,
                 event_id: EventId,
                 aggregate_id: AccountingDocumentId,
                 aggregate_version: int,
                 occurrence_date: datetime,
                 invoice_data: InvoiceData):
        super().__init__(event_id, aggregate_id, aggregate_version, occurrence_date)
        self.invoice_data = invoice_data

    def apply(self, aggregate):
        return aggregate.apply_invoice_added(self)

    @classmethod
    def create(cls,
               aggregate: AggregateRoot,
               invoice_data: InvoiceData) -> InvoiceAddedEvent:
        return InvoiceAddedEvent(
            event_id=EventId.new(),
            aggregate_id=AccountingDocumentId.of(aggregate.id),
            aggregate_version=aggregate.increment_version(),
            occurrence_date=current_datetime(),
            invoice_data=invoice_data
        )


class ChangeInvoiceDetailsEvent(DomainEvent):
    invoice_data: InvoiceData

    def __init__(self,
                 event_id: EventId,
                 aggregate_id: AccountingDocumentId,
                 aggregate_version: int,
                 occurrence_date: datetime,
                 invoice_data: InvoiceData):
        super().__init__(event_id, aggregate_id, aggregate_version, occurrence_date)
        self.invoice_data = invoice_data

    def apply(self, aggregate):
        return aggregate.apply_change_invoice_details(self)

    @classmethod
    def create(cls,
               aggregate: AggregateRoot,
               invoice_data: InvoiceData) -> ChangeInvoiceDetailsEvent:
        return ChangeInvoiceDetailsEvent(
            event_id=EventId.new(),
            aggregate_id=AccountingDocumentId.of(aggregate.id),
            aggregate_version=aggregate.increment_version(),
            occurrence_date=current_datetime(),
            invoice_data=invoice_data
        )


class DocumentAttachedEvent(DomainEvent):
    document_resource_id: CorrelationId

    def __init__(self,
                 event_id: EventId,
                 aggregate_id: AccountingDocumentId,
                 aggregate_version: int,
                 occurrence_date: datetime,
                 document_resource_id: CorrelationId):
        super().__init__(event_id, aggregate_id, aggregate_version, occurrence_date)
        self.document_resource_id = document_resource_id

    def apply(self, aggregate):
        return aggregate.apply_document_attached(self)

    @classmethod
    def create(cls,
               aggregate: AggregateRoot,
               document_resource_id: CorrelationId) -> DocumentAttachedEvent:
        return DocumentAttachedEvent(
            event_id=EventId.new(),
            aggregate_id=AccountingDocumentId.of(aggregate.id),
            aggregate_version=aggregate.increment_version(),
            occurrence_date=current_datetime(),
            document_resource_id=document_resource_id
        )
