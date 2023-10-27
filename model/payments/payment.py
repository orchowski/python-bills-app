from __future__ import annotations

from typing import TypeVar, Type, Tuple

from model.commons.aggregate_root import AggregateRoot
from model.commons.result import Fail, Result, Success
from model.commons.vo.correlation_id import CorrelationId
from model.commons.vo.money import Money
from model.payments.commands.payment_requested_command import PaymentRequestedCommand
from model.payments.payment_events import PaymentCompletedEvent, PaymentInitiatedEvent
from model.payments.vo.payment_id import PaymentId
from model.payments.vo.transfer_recipient_data import TransferRecipientData

P = TypeVar('P', bound='Payment')


class Payment(AggregateRoot):
    payment_title: str
    money: Money
    correlation_id: CorrelationId
    transfer_recipient_data: TransferRecipientData

    def __init__(
            self,
            id: PaymentId,
            aggregate_version: int,
            correlation_id: CorrelationId,
            money: Money,
            payment_title: str,
            transfer_recipient_data: TransferRecipientData
    ):
        super().__init__(id, aggregate_version)
        self.payment_title = payment_title
        self.money = money
        self.correlation_id = correlation_id
        self.transfer_recipient_data = transfer_recipient_data

    def complete(self) -> Tuple[Payment, Result]:
        return (
            self.apply(
                PaymentCompletedEvent.create(self)
            ),
            Success()
        )

    # TODO: we have to go deeper to get to know how this process works with mbank. 
    # Some id is added to correlate after all? Or we have to do that?
    # def external_id_is_given(self) -> Tuple[Payment, Result]:
    #    return (self, Success())

    def abort(self) -> Tuple[Payment, Result]:
        return (self, Success())

    def fail(self) -> Tuple[Payment, Result]:
        return (self, Success())

    @classmethod
    def create_from_payment_requested_command(cls, command: PaymentRequestedCommand) -> Payment:
        return Payment.shell().apply(
            PaymentInitiatedEvent.create(
                aggregate_id=PaymentId.generate_new(),
                money=command.money,
                correlation_id=command.correlation_id,
                payment_title=command.payment_title,
                transfer_recipient_data=command.transfer_recipient_data
            )
        )

    def apply_payment_init(self, event: PaymentInitiatedEvent) -> Payment:
        return Payment(
            PaymentId.of(event.aggregate_id),
            event.aggregate_version,
            event.correlation_id,
            event.money,
            event.payment_title,
            event.transfer_recipient_data
        )

    def apply_payment_completed(self, event: PaymentCompletedEvent) -> Payment:
        payment_to_apply = FinishedPayment.copy(self)
        payment_to_apply.aggregate_version = event.aggregate_version
        return payment_to_apply

    @classmethod
    def shell(cls: Type[P]) -> P:
        return cls(None, None, None, None, None, None)

    @classmethod
    def copy(cls: Type[P], another_payment: Payment) -> P:
        return cls(
            PaymentId.of(another_payment.id),
            another_payment.aggregate_version,
            correlation_id=another_payment.correlation_id,
            money=another_payment.money,
            payment_title=another_payment.payment_title,
            transfer_recipient_data=another_payment.transfer_recipient_data
        )


class FinishedPayment(Payment):
    def complete(self) -> Tuple[Payment, Result]:
        return (self, Fail("already finished"))

    def abort(self) -> Tuple[Payment, Result]:
        return (self, Fail("already finished"))

    def fail(self) -> Tuple[Payment, Result]:
        return (self, Fail("already finished"))
