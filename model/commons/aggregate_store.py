from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

import infrastructure.logger as logger
from model.commons.aggregate_root import AggregateId, AggregateRoot, DomainEvent
from model.commons.result import Result, Success


class AggregateStore(ABC):
    __event_publisher: EventPublisher

    def __init__(self, event_publisher: EventPublisher):
        self.__event_publisher = event_publisher

    @abstractmethod
    def save(self, aggregate_root: AggregateRoot) -> Result:
        if not isinstance(aggregate_root, AggregateRoot):
            raise TypeError("aggregate_root should be type of AggregateRoot")

        pass
        return Success()

    @abstractmethod
    def get_by(self, aggregate_id: AggregateId) -> AggregateRoot:
        if not isinstance(aggregate_id, AggregateId):
            raise TypeError("id should be type of AggregateId")
        pass

    def publish_all(self, new_events: List[DomainEvent]):
        for event in new_events:
            self.publish(event)

    def publish(self, new_event: DomainEvent):
        try:
            self.__event_publisher.publish(new_event)
        except Exception as e:
            logger.warn('Error "%s" during publishing event %s', e, new_event.id)


class EventPublisher(ABC):
    @abstractmethod
    def publish(self, event: DomainEvent):
        if not isinstance(event, DomainEvent):
            raise TypeError("event should be type of DomainEvent")
