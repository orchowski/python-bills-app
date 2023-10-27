from __future__ import annotations

from application.event_publisher import EventHandler
from infrastructure.db.commitment_read_model_repository import CommitmentReadModelRepository
from model.commitments.events import CommitmentRepeatPeriodChangedEvent


class OnCommitmentRepeatPeriodChangedUpdateCommitmentReadModelHandler(EventHandler):
    __commitments_read_model_repo: CommitmentReadModelRepository

    def __init__(self, commitment_read_model_repository: CommitmentReadModelRepository):
        super().__init__()
        self.__commitments_read_model_repo = commitment_read_model_repository

    def handle(self, event: CommitmentRepeatPeriodChangedEvent):
        super().handle(event)
        if not isinstance(event, CommitmentRepeatPeriodChangedEvent):
            return
        commitment = self.__commitments_read_model_repo.get_by_id(str(event.aggregate_id))
        if commitment:
            commitment.repeat_period = event.repeat_period.period
            commitment.start_date = event.repeat_period.start_date
            commitment.every_period = event.repeat_period.every
            commitment.modification_date = event.occurrence_date
            self.__commitments_read_model_repo.update(commitment)
