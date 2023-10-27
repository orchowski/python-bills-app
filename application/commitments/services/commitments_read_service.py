from typing import List

from application.commitments.readmodel.commitment import CommitmentReadModel
from infrastructure.db.commitment_read_model_repository import CommitmentReadModelRepository
from model.commons.vo.context import Context


class CommitmentsReadService:
    __commitments_rm_repo: CommitmentReadModelRepository

    def __init__(self, commitments_repository: CommitmentReadModelRepository):
        self.__commitments_rm_repo = commitments_repository

    def get_all(self, context: Context) -> List[CommitmentReadModel]:
        return self.__commitments_rm_repo.get_all(context)
