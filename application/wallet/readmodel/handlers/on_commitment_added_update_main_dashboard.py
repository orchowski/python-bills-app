import datetime
from typing import List

from application.event_publisher import EventHandler
from application.wallet.readmodel.main_dashboard import MainDashboardReadModel, CommitmentDashboardRM
from infrastructure.db.wallet.main_dashboard_read_model_repository import MainDashboardReadModelRepository
from model.commitments.events import CommitmentAddedEvent
from model.commitments.services.commitments_in_period_service import CommitmentsInPeriodService
from model.commitments.services.params.commitments_calculation_data import CyclicCommitmentDefinition, OccurrenceRange
from model.commons.time import current_date


class OnCommitmentAddedEventUpdateMainDashboard(EventHandler):
    __dashboard_read_model_repo: MainDashboardReadModelRepository
    __commitments_in_period_srv: CommitmentsInPeriodService

    def __init__(self,
                 read_model_repository: MainDashboardReadModelRepository,
                 commitments_in_period_srv: CommitmentsInPeriodService):
        super().__init__()
        self.__dashboard_read_model_repo = read_model_repository
        self.__commitments_in_period_srv = commitments_in_period_srv

    def handle(self, event: CommitmentAddedEvent):
        super().handle(event)
        if not isinstance(event, CommitmentAddedEvent):
            return
        dashboard = self.__dashboard_read_model_repo.get_by_wallet_id(str(event.wallet_id))
        if dashboard is None:
            dashboard = MainDashboardReadModel(str(event.wallet_id))
        dashboard.commitments_upcoming += self.calculate_upcoming_commitment_occurrences(event)
        self.__dashboard_read_model_repo.save(dashboard)

    def calculate_upcoming_commitment_occurrences(self, event) -> List[CommitmentDashboardRM]:
        if not event.active:
            return []
        cyclic_def = CyclicCommitmentDefinition(
            commitment_id=str(event.aggregate_id),
            repeat_period=event.repeat_period
        )
        return [CommitmentDashboardRM(id=cyclic_def.a_id,
                                      deadline=commitment_occurrence_to_add,
                                      money=event.amount,
                                      unit=str(event.unit),
                                      title=event.metadata.title
                                      ) for commitment_occurrence_to_add in
                self.__commitments_in_period_srv.occurrences_of_given_in_range(
                    of=[cyclic_def], a_range=OccurrenceRange(
                        after=current_date(),
                        before=current_date() + datetime.timedelta(days=10)
                    )
                ).get(cyclic_def)]
