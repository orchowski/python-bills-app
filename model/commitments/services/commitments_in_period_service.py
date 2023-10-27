from datetime import date
from functools import reduce
from typing import Dict
from typing import List

from infrastructure.db.commitment_read_model_repository import CommitmentReadModelRepository
from model.commitments.services.params.commitments_calculation_data import OccurrenceRange, CommitmentDefinition, \
    CyclicCommitmentDefinition
from model.commitments.vo.repeat_period import RepeatPeriod
from model.commons.vo.context import Context
from application.commitments.readmodel.commitment import CommitmentReadModel


class CommitmentsInPeriodService:
    __commitments_repo: CommitmentReadModelRepository

    def __init__(self, repo: CommitmentReadModelRepository):
        self.__commitments_repo = repo

    @staticmethod
    def __commitment_rm_to_definition(commitment_rm: CommitmentReadModel) -> CommitmentDefinition:
        return CyclicCommitmentDefinition.create(
            id=commitment_rm.id,
            repeat_period=RepeatPeriod(period=commitment_rm.repeat_period,
                                       start_date=commitment_rm.start_date,
                                       every=commitment_rm.every_period)
        )

    def occurrences_in_range(self, context: Context, a_range: OccurrenceRange) \
            -> Dict[CommitmentDefinition, List[date]]:
        commitments = self.__commitments_repo.get_all(context)
        return self.occurrences_of_given_in_range([self.__commitment_rm_to_definition(commitment)
                                                   for commitment in commitments],
                                                  a_range)

    @staticmethod
    def occurrences_of_given_in_range(of: List[CommitmentDefinition], a_range: OccurrenceRange) \
            -> Dict[CommitmentDefinition, List[date]]:
        return reduce(lambda result, prev: result | prev,
                      map(lambda payment: payment.occurrences_in(a_range), of))
