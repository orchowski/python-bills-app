from typing import List

from application.commitments.readmodel.commitment import CommitmentReadModel
from model.commons.vo.context import Context

class TestCommitmentReadModelRepository:
    __test__ = False

    commitments: List[CommitmentReadModel] = []

    def save(self, commitment: CommitmentReadModel):
        self.commitments.append(commitment)

    def update(self, commitment: CommitmentReadModel):
        self.delete(
            self.get_by_id(commitment.id).id
        )
        self.save(commitment)

    def delete(self, id: str):
        self.commitments.remove(self.get_by_id(id))

    def get_all(self, context: Context) -> List[CommitmentReadModel]:
        return [
            commitment for commitment in self.commitments
            if commitment.active and commitment.wallet_id == str(context.wallet.id)
        ]

    def get_by_id(self, id: str) -> CommitmentReadModel:
        hits = list(filter(lambda bill: bill.id == id, self.get_all()))

        if len(hits) == 0:
            raise ValueError("there is no such element")
        if len(hits) != 1:
            raise ValueError("duplicates found, data corrupted")
        return hits[0]