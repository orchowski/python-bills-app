from __future__ import annotations

from application.event_publisher import EventHandler
from infrastructure.db.commitment_read_model_repository import CommitmentReadModelRepository
from model.commitments.events import CommitmentAddedEvent
from application.commitments.readmodel.commitment import CommitmentReadModel


class OnAddCommitmentEventUpdateCommitmentReadModel(EventHandler):
    __commitments_read_model_repo: CommitmentReadModelRepository

    def __init__(self, read_model_repository: CommitmentReadModelRepository):
        super().__init__()
        self.__commitments_read_model_repo = read_model_repository

    def handle(self, event: CommitmentAddedEvent):
        super().handle(event)
        if not isinstance(event, CommitmentAddedEvent):
            return
        self.__commitments_read_model_repo.save(CommitmentReadModel.of(event))
