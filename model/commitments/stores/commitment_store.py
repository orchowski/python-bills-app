from abc import abstractmethod

from model.commitments.commitment import Commitment, CommitmentId
from model.commons.aggregate_store import AggregateStore
from model.commons.result import Result, Success


class CommitmentStore(AggregateStore):

    @abstractmethod
    def save(self, commitment: Commitment) -> Result:
        super().save(commitment)
        if not isinstance(commitment, Commitment):
            raise TypeError("commitment should be type of Commitment")
        return Success()

    @abstractmethod
    def get_by(self, commitmentId: CommitmentId) -> Commitment:
        if not isinstance(commitmentId, CommitmentId):
            raise TypeError("commitmentId should be type of CommitmentId")
        pass
