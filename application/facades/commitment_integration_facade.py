from typing import Optional, List, Tuple

from application.commitments.readmodel.commitment import CommitmentReadModel
from application.commitments.services.commitments_read_service import CommitmentsReadService
from model.commitments.commands.add_commitment import AddCommitment
from model.commitments.commands.update_commitment import UpdateCommitment
from model.commitments.services.commitment_service import CommitmentService
from model.commitments.stores.commitment_store import CommitmentStore
from model.commitments.vo.commitment_id import CommitmentId
from model.commons.result import Result
from model.commons.vo.context import Context


class CommitmentIntegrationFacade:

    def __init__(self,
                 domain_service: CommitmentService,
                 commitment_store: CommitmentStore,
                 commitment_read_service: CommitmentsReadService):
        self.__domain = domain_service
        self.__commitment_store = commitment_store
        self.__commitments_read_service = commitment_read_service

    def get_all(self, context: Context) -> List[CommitmentReadModel]:
        return self.__commitments_read_service.get_all(context)

    def add_new_commitment(self, command: AddCommitment) -> Tuple[Optional[CommitmentId], Result]:
        return self.__domain.add(command)

    def update_commitment(self, command: UpdateCommitment) -> Result:
        return self.__domain.update(command)
