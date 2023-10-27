from __future__ import annotations

from datetime import date, datetime
from typing import TypeVar, Type, Optional, Tuple

from model.commons.aggregate_root import AggregateRoot
from model.commons.result import Result, Fail, Success
from model.commons.time import current_datetime
from model.commons.vo.correlation_id import CorrelationId
from model.commons.vo.money import Money
from model.payments.commands.create_payment_demand import CreatePaymentDemand
from model.payments.payment_demand_events import PaymentDemandInitiatedEvent, PaymentDemandSatisfyRequestedEvent
from model.payments.policies.transfer_title_policies import TransferTitleGenerationPolicy
from model.payments.vo.payment_demand_id import PaymentDemandId
from model.payments.vo.transfer_recipient_data import TransferRecipientData

PD = TypeVar('PD', bound='PaymentDemand')


class PaymentDemand(AggregateRoot):
    correlation_id: CorrelationId
    money: Money
    payment_deadline: date
    transfer_recipient_data: TransferRecipientData
    request_number: int
    request_date: Optional[datetime]

    def __init__(
            self,
            id: PaymentDemandId,
            aggregate_version: int,
            correlation_id: CorrelationId,
            money: Money,
            payment_deadline: date,
            transfer_recipient_data: TransferRecipientData,
            request_number: int,
            request_date: Optional[datetime] = None):
        super().__init__(id, aggregate_version)
        self.correlation_id = correlation_id
        self.money = money
        self.payment_deadline = payment_deadline
        self.transfer_recipient_data = transfer_recipient_data
        self.request_number = request_number
        self.request_date = request_date

    def satisfy(self, title_policy: TransferTitleGenerationPolicy) -> Tuple[Optional[PaymentDemand], Result]:
        if self.request_date is not None and (self.request_date - current_datetime()).days < 2:
            return None, Fail("you have to wait to retry payment")
        return self.apply(PaymentDemandSatisfyRequestedEvent.create(
            self,
            self.money,
            self.correlation_id,
            title_policy.generate(),
            self.transfer_recipient_data,
            self.request_number + 1)), Success()

    def apply_payment_demand_init(self, event: PaymentDemandInitiatedEvent) -> PaymentDemand:
        return PaymentDemand(
            PaymentDemandId.of(event.aggregate_id),
            event.aggregate_version,
            event.correlation_id,
            event.money,
            event.payment_deadline,
            event.transfer_recipient_data,
            0
        )

    def apply_payment_demand_satisfy_requested(self, event: PaymentDemandSatisfyRequestedEvent) -> PaymentDemand:
        demand_to_apply = self.copy(self)
        demand_to_apply.request_number = event.request_number
        demand_to_apply.request_date = event.occurrence_date
        demand_to_apply.aggregate_version = event.aggregate_version
        return demand_to_apply

    @classmethod
    def create_from_payment_demand_command(cls, command: CreatePaymentDemand) -> PaymentDemand:
        return PaymentDemand.shell().apply(
            PaymentDemandInitiatedEvent.create(
                aggregate_id=PaymentDemandId.generate_new(),
                purpose=command.purpose,
                money=command.money,
                payment_deadline=command.payment_deadline,
                correlation_id=command.correlation_id,
                transfer_recipient_data=command.transfer_recipient_data
            )
        )

    @classmethod
    def shell(cls: Type[PD]) -> PD:
        return cls(None, None, None, None, None, None, None)

    @classmethod
    def copy(cls: Type[PD], another_payment_demand: PaymentDemand) -> PD:
        return cls(
            PaymentDemandId.of(another_payment_demand.id),
            another_payment_demand.aggregate_version,
            another_payment_demand.correlation_id,
            another_payment_demand.money,
            another_payment_demand.payment_deadline,
            another_payment_demand.transfer_recipient_data,
            another_payment_demand.request_number,
            another_payment_demand.request_date
        )
