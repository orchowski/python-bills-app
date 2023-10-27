from typing import List

from application.event_publisher import EventHandler
from model.commons.aggregate_root import DomainEvent


class RegisteringEventHandler(EventHandler):
    achieved_events: List[DomainEvent] = []

    def __init__(self) -> None:
        super().__init__()
        self.achieved_events = []

    def handle(self, event: DomainEvent):
        self.achieved_events.append(event)
