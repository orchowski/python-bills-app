from __future__ import annotations

from functools import reduce
from typing import Type, TypeVar, Tuple

from model.commitments.commands.add_commitment import AddCommitment
from model.commitments.commands.update_commitment import UpdateCommitment
from model.commitments.events import CommitmentActivatedEvent, CommitmentAddedEvent, CommitmentAmountChangedEvent, \
    CommitmentDeactivatedEvent, CommitmentMetadataUpdatedEvent, CommitmentRepeatPeriodChangedEvent
from model.commitments.vo.commitment_id import CommitmentId
from model.commitments.vo.repeat_period import RepeatPeriod
from model.commons.aggregate_root import AggregateRoot
from model.commons.result import Result, Success
from model.commons.vo.money import Money
from model.commons.vo.unit import Unit
from model.commons.vo.context import WalletId

C = TypeVar('C', bound='Commitment')


class Commitment(AggregateRoot):
    amount: Money
    repeat_period: RepeatPeriod

    def __init__(self,
                 id: CommitmentId,
                 aggregate_version: int,
                 amount: Money,
                 repeat_period: RepeatPeriod,
                 wallet_id: WalletId):
        super().__init__(id, aggregate_version)
        self.amount = amount
        self.repeat_period = repeat_period
        self.wallet_id = wallet_id

    def update_with(self, command: UpdateCommitment) -> Tuple[Commitment, Result]:
        update_events = []
        update_events.append(
            CommitmentMetadataUpdatedEvent.create(self, command.metadata))

        if self.amount.amount != command.amount or self.amount.unit != Unit(command.unit):
            update_events.append(CommitmentAmountChangedEvent.create(
                self, command.amount, Unit(command.unit)))

        new_repeat_period = RepeatPeriod(
            start_date=command.start_date,
            period=command.repeat_period,
            every=command.every_period
        )
        if self.repeat_period != new_repeat_period:
            update_events.append(
                CommitmentRepeatPeriodChangedEvent.create(self, new_repeat_period))

        return (reduce(lambda acc, event: acc.apply(event), update_events, self), Success())

    def apply_add(self, event: CommitmentAddedEvent) -> Commitment:
        commitment_init = ActiveCommitment if event.active else InActiveCommitment
        return commitment_init(
            id=CommitmentId.of(event.aggregate_id),
            aggregate_version=1,
            amount=Money(event.amount, event.unit),
            repeat_period=event.repeat_period,
            wallet_id=event.wallet_id
        )

    def apply_amount_changed(self, event: CommitmentAmountChangedEvent) -> Commitment:
        commitment_to_apply = self.copy(self)
        commitment_to_apply.amount = Money(event.amount, event.unit)
        commitment_to_apply.aggregate_version = event.aggregate_version
        return commitment_to_apply

    def apply_repeat_period(self, event: CommitmentRepeatPeriodChangedEvent) -> Commitment:
        commitment_to_apply = self.copy(self)
        commitment_to_apply.repeat_period = event.repeat_period
        commitment_to_apply.aggregate_version = event.aggregate_version
        return commitment_to_apply

    def apply_metadata(self, event: CommitmentMetadataUpdatedEvent) -> Commitment:
        self.aggregate_version = event.aggregate_version
        return self

    @classmethod
    def from_add_commitment_command(cls: Type[C], command: AddCommitment) -> Commitment:
        aggregate_id = CommitmentId.generate_new()
        add = CommitmentAddedEvent.create(
            aggregate_id=aggregate_id,
            amount=command.amount,
            unit=Unit(command.unit),
            metadata=command.metadata,
            active=command.active,
            wallet_id=command.context.wallet,
            repeat_period=RepeatPeriod(
                start_date=command.start_date,
                period=command.repeat_period,
                every=command.every_period
            )
        )
        return Commitment.shell().apply(
            add
        )

    @classmethod
    def shell(cls: Type[C]) -> C:
        return cls(None, None, None, None, None)

    @classmethod
    def copy(cls: Type[C], another_commitment: Commitment) -> C:
        return cls(
            CommitmentId.of(another_commitment.id),
            another_commitment.aggregate_version,
            another_commitment.amount,
            another_commitment.repeat_period,
            another_commitment.wallet_id)


class ActiveCommitment(Commitment):
    def update_with(self, command: UpdateCommitment) -> Tuple[Commitment, Result]:
        to_update = (self.apply(CommitmentDeactivatedEvent.create(self))
                     if not command.active else self)
        return super(type(to_update), to_update).update_with(command)

    def apply_deactivate(self, event: CommitmentDeactivatedEvent) -> InActiveCommitment:
        self.aggregate_version = event.aggregate_version
        return InActiveCommitment.copy(self)


class InActiveCommitment(Commitment):

    def update_with(self, command: UpdateCommitment) -> Tuple[Commitment, Result]:
        to_update = (self.apply(CommitmentActivatedEvent.create(self))
                     if command.active else self)
        return super(type(to_update), to_update).update_with(command)

    def apply_activate(self, event: CommitmentDeactivatedEvent) -> ActiveCommitment:
        self.aggregate_version = event.aggregate_version
        return ActiveCommitment.copy(self)
