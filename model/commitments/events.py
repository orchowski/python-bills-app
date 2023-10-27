from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from model.commitments.vo.commitment_id import CommitmentId
from model.commitments.vo.metadata import Metadata
from model.commitments.vo.repeat_period import RepeatPeriod
from model.commons.aggregate_root import AggregateRoot, DomainEvent, EventId
from model.commons.time import current_datetime
from model.commons.vo.unit import Unit
from model.commons.vo.context import WalletId


class CommitmentAddedEvent(DomainEvent):
    amount: Decimal
    unit: Unit
    metadata: Metadata
    repeat_period: RepeatPeriod
    every_period: int
    active: bool
    wallet_id: WalletId

    def __init__(self,
                 event_id: EventId,
                 aggregate_id: CommitmentId,
                 aggregate_version: int,
                 wallet_id: WalletId,
                 occurrence_date: datetime,
                 amount: Decimal,
                 unit: Unit,
                 metadata: Metadata,
                 repeat_period: RepeatPeriod,
                 active: bool
                 ):
        super().__init__(event_id, aggregate_id, aggregate_version, occurrence_date)
        self.amount = amount
        self.unit = unit
        self.wallet_id = wallet_id
        self.metadata = metadata
        self.repeat_period = repeat_period
        self.active = active

    def apply(self, aggregate_root):
        return aggregate_root.apply_add(self)

    @classmethod
    def create(cls,
               aggregate_id: CommitmentId,
               amount: Decimal,
               wallet_id: WalletId,
               metadata: Metadata,
               unit: Unit,
               repeat_period: RepeatPeriod,
               active: bool) -> CommitmentAddedEvent:
        event = CommitmentAddedEvent(
            event_id=EventId.new(),
            aggregate_id=aggregate_id,
            aggregate_version=1,
            occurrence_date=current_datetime(),
            amount=amount,
            wallet_id=wallet_id,
            unit=unit,
            metadata=metadata,
            repeat_period=repeat_period,
            active=active
        )
        return event


class CommitmentAmountChangedEvent(DomainEvent):
    amount: Decimal
    unit: Unit

    def __init__(self,
                 event_id: EventId,
                 aggregate_id: CommitmentId,
                 aggregate_version: int,
                 occurrence_date: datetime,
                 amount: Decimal,
                 unit: Unit
                 ):
        super().__init__(event_id, aggregate_id, aggregate_version, occurrence_date)
        self.amount = amount
        self.unit = unit

    def apply(self, aggregate_root):
        return aggregate_root.apply_amount_changed(self)

    @classmethod
    def create(cls,
               aggregate: AggregateRoot,
               amount: Decimal,
               unit: Unit
               ) -> CommitmentAmountChangedEvent:
        event = CommitmentAmountChangedEvent(
            event_id=EventId.new(),
            aggregate_id=CommitmentId.of(aggregate.id),
            aggregate_version=aggregate.increment_version(),
            occurrence_date=current_datetime(),
            amount=amount,
            unit=unit
        )
        return event


class CommitmentRepeatPeriodChangedEvent(DomainEvent):
    repeat_period: RepeatPeriod

    def __init__(self,
                 event_id: EventId,
                 aggregate_id: CommitmentId,
                 aggregate_version: int,
                 occurrence_date: datetime,
                 repeat_period: RepeatPeriod
                 ):
        super().__init__(event_id, aggregate_id, aggregate_version, occurrence_date)
        self.repeat_period = repeat_period

    def apply(self, aggregate_root):
        return aggregate_root.apply_repeat_period(self)

    @classmethod
    def create(cls,
               aggregate: AggregateRoot,
               repeat_period: RepeatPeriod
               ) -> CommitmentRepeatPeriodChangedEvent:
        event = CommitmentRepeatPeriodChangedEvent(
            event_id=EventId.new(),
            aggregate_id=CommitmentId.of(aggregate.id),
            aggregate_version=aggregate.increment_version(),
            occurrence_date=current_datetime(),
            repeat_period=repeat_period
        )
        return event


class CommitmentMetadataUpdatedEvent(DomainEvent):
    metadata: Metadata

    def __init__(self,
                 event_id: EventId,
                 aggregate_id: CommitmentId,
                 aggregate_version: int,
                 occurrence_date: datetime,
                 metadata: Metadata
                 ):
        super().__init__(event_id, aggregate_id, aggregate_version, occurrence_date)
        self.metadata = metadata

    def apply(self, aggregate_root):
        return aggregate_root.apply_metadata(self)

    @classmethod
    def create(cls,
               aggregate: AggregateRoot,
               metadata: Metadata
               ) -> CommitmentMetadataUpdatedEvent:
        event = CommitmentMetadataUpdatedEvent(
            event_id=EventId.new(),
            aggregate_id=CommitmentId.of(aggregate.id),
            aggregate_version=aggregate.increment_version(),
            occurrence_date=current_datetime(),
            metadata=metadata
        )
        return event


class CommitmentDeactivatedEvent(DomainEvent):
    def __init__(self,
                 event_id: EventId,
                 aggregate_id: CommitmentId,
                 aggregate_version: int,
                 occurrence_date: datetime
                 ):
        super().__init__(event_id, aggregate_id, aggregate_version, occurrence_date)

    def apply(self, aggregate_root):
        return aggregate_root.apply_deactivate(self)

    @classmethod
    def create(cls,
               aggregate: AggregateRoot) -> CommitmentDeactivatedEvent:
        event = CommitmentDeactivatedEvent(
            event_id=EventId.new(),
            aggregate_id=CommitmentId.of(aggregate.id),
            aggregate_version=aggregate.increment_version(),
            occurrence_date=current_datetime()
        )
        return event


class CommitmentActivatedEvent(DomainEvent):
    metadata: Metadata

    def __init__(self,
                 event_id: EventId,
                 aggregate_id: CommitmentId,
                 aggregate_version: int,
                 occurrence_date: datetime
                 ):
        super().__init__(event_id, aggregate_id, aggregate_version, occurrence_date)

    def apply(self, aggregate_root):
        return aggregate_root.apply_activate(self)

    @classmethod
    def create(cls,
               aggregate: AggregateRoot) -> CommitmentActivatedEvent:
        event = CommitmentActivatedEvent(
            event_id=EventId.new(),
            aggregate_id=CommitmentId.of(aggregate.id),
            aggregate_version=aggregate.increment_version(),
            occurrence_date=current_datetime()
        )
        return event
