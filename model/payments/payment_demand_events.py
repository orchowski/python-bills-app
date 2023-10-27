from __future__ import annotations

from datetime import datetime, date

from model.commons.aggregate_root import AggregateRoot, DomainEvent, EventId
from model.commons.time import current_datetime
from model.commons.vo.correlation_id import CorrelationId
from model.commons.vo.money import Money
from model.payments.vo.payment_demand_id import PaymentDemandId
from model.payments.vo.purpose import Purpose
from model.payments.vo.transfer_recipient_data import TransferRecipientData


class PaymentDemandInitiatedEvent(DomainEvent):
    money: Money
    payment_deadline: date
    purpose: Purpose
    correlation_id: CorrelationId
    transfer_recipient_data: TransferRecipientData

    def apply(self, aggregate_root):
        return aggregate_root.apply_payment_demand_init(self)

    def __init__(self,
                 event_id: EventId,
                 aggregate_id: PaymentDemandId,
                 aggregate_version: int,
                 occurrence_date: datetime,
                 money: Money,
                 payment_deadline: date,
                 purpose: Purpose,
                 correlation_id: CorrelationId,
                 transfer_recipient_data: TransferRecipientData
                 ):
        super().__init__(event_id, aggregate_id, aggregate_version, occurrence_date)
        self.money = money
        self.payment_deadline = payment_deadline
        self.purpose = purpose
        self.correlation_id = correlation_id
        self.transfer_recipient_data = transfer_recipient_data

    @classmethod
    def create(cls,
               aggregate_id: PaymentDemandId,
               money: Money,
               payment_deadline: date,
               purpose: Purpose,
               correlation_id: CorrelationId,
               transfer_recipient_data: TransferRecipientData
               ) -> PaymentDemandInitiatedEvent:
        return cls(
            event_id=EventId.new(),
            aggregate_id=aggregate_id,
            aggregate_version=1,
            occurrence_date=current_datetime(),
            money=money,
            payment_deadline=payment_deadline,
            purpose=purpose,
            correlation_id=correlation_id,
            transfer_recipient_data=transfer_recipient_data
        )


class PaymentDemandSatisfyRequestedEvent(DomainEvent):
    payment_title: str
    money: Money
    correlation_id: CorrelationId
    transfer_recipient_data: TransferRecipientData
    request_number: int

    def apply(self, aggregate_root):
        return aggregate_root.apply_payment_demand_satisfy_requested(self)

    def __init__(self,
                 event_id: EventId,
                 aggregate_id: PaymentDemandId,
                 aggregate_version: int,
                 occurrence_date: datetime,
                 money: Money,
                 correlation_id: CorrelationId,
                 payment_title: str,
                 transfer_recipient_data: TransferRecipientData,
                 request_number: int
                 ):
        super().__init__(event_id, aggregate_id, aggregate_version, occurrence_date)
        self.payment_title = payment_title
        self.money = money
        self.correlation_id = correlation_id
        self.transfer_recipient_data = transfer_recipient_data
        self.request_number = request_number

    @classmethod
    def create(cls,
               aggregate: AggregateRoot,
               money: Money,
               correlation_id: CorrelationId,
               payment_title: str,
               transfer_recipient_data: TransferRecipientData,
               request_number: int
               ) -> PaymentDemandSatisfyRequestedEvent:
        return cls(
            event_id=EventId.new(),
            aggregate_id=PaymentDemandId.of(aggregate.id),
            aggregate_version=aggregate.increment_version(),
            occurrence_date=current_datetime(),
            payment_title=payment_title,
            money=money,
            correlation_id=correlation_id,
            transfer_recipient_data=transfer_recipient_data,
            request_number=request_number
        )
