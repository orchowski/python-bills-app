from typing import Tuple

from model.commitments.commands.add_commitment import AddCommitment
from model.commitments.commands.update_commitment import UpdateCommitment
from model.commitments.commitment import Commitment
from model.commitments.stores.commitment_store import CommitmentStore
from model.commitments.vo.commitment_id import CommitmentId
from model.commons.result import Result, Fail


class CommitmentService:
    def __init__(self, store: CommitmentStore):
        if not isinstance(store, CommitmentStore):
            raise TypeError(CommitmentStore)
        self.__store = store

    def add(self, command: AddCommitment) -> Tuple[CommitmentId, Result]:
        new_commitment = Commitment.from_add_commitment_command(command)
        return new_commitment.id, self.__store.save(
            new_commitment
        )

    def update(self, command: UpdateCommitment) -> Result:
        commitment: Commitment = self.__store.get_by(command.id)
        if commitment.wallet_id != command.context.wallet:
            return Fail("commitment not found in given context")
        commitment, result = commitment.update_with(command)
        if result.succeded():
            return self.__store.save(
                commitment
            )
        return result
