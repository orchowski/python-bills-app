from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import List
from typing import Type, TypeVar
from uuid import uuid4, UUID

T = TypeVar('T', bound='AggregateId')
A = TypeVar('A', bound='AggregateRoot')
D = TypeVar('D', bound='DomainEvent')


class AggregateRoot(ABC):
    __newly_applied_events: List[DomainEvent] = []
    id: T
    aggregate_version: int

    def increment_version(self) -> int:
        self.aggregate_version += 1
        return self.aggregate_version

    def __init__(self, id: T, aggregate_version: int):
        self.id = id
        self.aggregate_version = aggregate_version
        super().__init__()

    def apply(self: A, domain_event: D) -> A:
        if not isinstance(domain_event, DomainEvent):
            raise TypeError("domain_event should be type of DomainEvent")
        new_aggregate = domain_event.apply(self)
        new_aggregate.aggregate_version = domain_event.aggregate_version
        new_aggregate.__newly_applied_events = self.__newly_applied_events.copy()
        new_aggregate.__newly_applied_events.append(domain_event)
        return new_aggregate

    def extract_events_with_state_clearing(self) -> List[DomainEvent]:
        events_copy = list(self.__newly_applied_events)
        self.__newly_applied_events.clear()
        return events_copy


class AggregateId(ABC):
    __id: UUID

    def __init__(self, id: UUID):
        if not isinstance(id, UUID):
            raise ValueError(UUID)
        self.__id = id

    @classmethod
    def generate_new(cls: Type[T]) -> T:
        return cls(uuid4())

    @classmethod
    def of(cls: Type[T], id: AggregateId) -> T:
        return cls(UUID(str(id)))

    def __repr__(self) -> str:
        return str(self.__id)

    def __eq__(self, o) -> bool:
        if type(self) == type(o):
            return self.__id == o.__id
        return False

    def __hash__(self) -> int:
        return hash(self.__id)


class DomainEvent(ABC):
    id: EventId
    aggregate_id: AggregateId
    aggregate_version: int
    occurrence_date: datetime

    def __init__(self, event_id: EventId, aggregate_id: AggregateId, aggregate_version: int, occurrence_date: datetime):
        super().__init__()
        self.id = event_id
        self.aggregate_id = aggregate_id
        self.aggregate_version = aggregate_version
        self.occurrence_date = occurrence_date

    def apply(self, aggregate_root: A) -> A:
        raise NotImplementedError()

    def __eq__(self, o: object) -> bool:
        return (isinstance(o, DomainEvent)
                and o.aggregate_version == self.aggregate_version
                and o.aggregate_id == self.aggregate_id
                )

    def __hash__(self):
        return hash((self.aggregate_id, self.aggregate_version))


@dataclass(frozen=True)
class EventId:
    __value: UUID

    def uuid(self) -> UUID:
        return self.__value

    @classmethod
    def new(cls) -> EventId:
        return cls(uuid4())
