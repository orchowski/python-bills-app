from __future__ import annotations

from application.event_publisher import EventHandler
from infrastructure.db.commitment_read_model_repository import CommitmentReadModelRepository
from model.commitments.events import CommitmentMetadataUpdatedEvent


class OnCommitmentMetadataUpdatedUpdateCommitmentReadModelHandler(EventHandler):
    __commitment_read_model_repo: CommitmentReadModelRepository

    def __init__(self, commitment_read_model_repository: CommitmentReadModelRepository):
        super().__init__()
        self.__commitment_read_model_repo = commitment_read_model_repository

    def handle(self, event: CommitmentMetadataUpdatedEvent):
        super().handle(event)
        if not isinstance(event, CommitmentMetadataUpdatedEvent):
            return
        commitment = self.__commitment_read_model_repo.get_by_id(str(event.aggregate_id))
        if commitment:
            commitment.title = event.metadata.title
            commitment.description = event.metadata.description
            commitment.modification_date = event.occurrence_date
            self.__commitment_read_model_repo.update(commitment)
