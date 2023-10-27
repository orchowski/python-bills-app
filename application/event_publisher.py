from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from model.commons.aggregate_root import DomainEvent
from model.commons.aggregate_store import EventPublisher


class DefaultEventPublisher(EventPublisher):
    __event_handlers: List[EventHandler] = []

    def __init__(self, event_handlers: List[EventHandler]) -> None:
        super().__init__()
        self.__event_handlers = event_handlers

    def publish(self, event: DomainEvent):
        super().publish(event)
        for handler in self.__event_handlers:
            handler.handle(event)

    def register(self, event_handlers: List[EventHandler]):
        self.__event_handlers = self.__event_handlers + event_handlers


class EventHandler(ABC):
    @abstractmethod
    def handle(self, event: DomainEvent):
        if not isinstance(event, DomainEvent):
            raise TypeError("event should be type of DomainEvent")
