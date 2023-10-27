from __future__ import annotations

from datetime import datetime

from model.commons.aggregate_root import DomainEvent, EventId, AggregateRoot
from model.commons.time import current_datetime
from model.commons.vo.correlation_id import CorrelationId
from model.commons.vo.money import Money
from model.payments.vo.payment_id import PaymentId
from model.payments.vo.transfer_recipient_data import TransferRecipientData


class PaymentInitiatedEvent(DomainEvent):
    payment_title: str
    money: Money
    correlation_id: CorrelationId
    transfer_recipient_data: TransferRecipientData

    def apply(self, aggregate_root):
        return aggregate_root.apply_payment_init(self)

    def __init__(self,
                 event_id: EventId,
                 aggregate_id: PaymentId,
                 aggregate_version: int,
                 occurrence_date: datetime,
                 money: Money,
                 correlation_id: CorrelationId,
                 payment_title: str,
                 transfer_recipient_data: TransferRecipientData,
                 ):
        super().__init__(event_id, aggregate_id, aggregate_version, occurrence_date)
        self.payment_title = payment_title
        self.money = money
        self.correlation_id = correlation_id
        self.transfer_recipient_data = transfer_recipient_data

    @classmethod
    def create(cls,
               aggregate_id: PaymentId,
               money: Money,
               correlation_id: CorrelationId,
               payment_title: str,
               transfer_recipient_data: TransferRecipientData,
               ) -> PaymentInitiatedEvent:
        return cls(
            event_id=EventId.new(),
            aggregate_id=aggregate_id,
            aggregate_version=1,
            occurrence_date=current_datetime(),
            payment_title=payment_title,
            money=money,
            correlation_id=correlation_id,
            transfer_recipient_data=transfer_recipient_data,
        )


class PaymentCompletedEvent(DomainEvent):

    def apply(self, aggregate_root):
        return aggregate_root.apply_payment_completed(self)

    def __init__(self,
                 event_id: EventId,
                 aggregate_id: PaymentId,
                 aggregate_version: int,
                 occurrence_date: datetime
                 ):
        super().__init__(event_id, aggregate_id, aggregate_version, occurrence_date)

    @classmethod
    def create(cls,
               aggregate: AggregateRoot,
               ) -> PaymentCompletedEvent:
        return cls(
            event_id=EventId.new(),
            aggregate_id=PaymentId.of(aggregate.id),
            aggregate_version=aggregate.increment_version(),
            occurrence_date=current_datetime()
        )
