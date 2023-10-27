from __future__ import annotations

from application.event_publisher import EventHandler
from infrastructure.db.commitment_read_model_repository import CommitmentReadModelRepository
from model.commitments.events import CommitmentDeactivatedEvent


class OnCommitmentDeactivatedUpdateCommitmentReadModelHandler(EventHandler):
    __commitment_read_model_repo: CommitmentReadModelRepository

    def __init__(self, commitment: CommitmentReadModelRepository):
        super().__init__()
        self.__commitment_read_model_repo = commitment

    def handle(self, event: CommitmentDeactivatedEvent):
        super().handle(event)
        if not isinstance(event, CommitmentDeactivatedEvent):
            return
        commitment = self.__commitment_read_model_repo.get_by_id(str(event.aggregate_id))
        if commitment:
            commitment.active = False
            commitment.modification_date = event.occurrence_date
            self.__commitment_read_model_repo.update(commitment)
