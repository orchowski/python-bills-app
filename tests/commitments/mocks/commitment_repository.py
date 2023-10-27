from functools import reduce
from typing import List

import infrastructure.logger as logger
from model.commitments.commitment import Commitment
from model.commitments.stores.commitment_store import CommitmentStore
from model.commitments.vo.commitment_id import CommitmentId
from model.commons.aggregate_root import DomainEvent
from model.commons.result import Fail, Result, Success


class TestCommitmentRepository(CommitmentStore):
    __test__ = False
    __commitment_events: List[DomainEvent] = []

    def save(self, commitment: Commitment) -> Result:
        try:
            super(TestCommitmentRepository, self).save(commitment)
            new_events = commitment.extract_events_with_state_clearing()
            print(new_events)
            self.__commitment_events = self.__commitment_events + new_events
            self.publish_all(new_events)
        except Exception as e:
            logger.error('Test commitment repo saving error %s', e)
            return Fail(e)
        return Success()

    def get_by(self, bill_id: CommitmentId) -> Commitment:
        super(TestCommitmentRepository, self).get_by(bill_id)
        aggregate_events = list(
            filter(lambda event: event.aggregate_id == bill_id, self.__commitment_events))
        return reduce(lambda commitment, event: event.apply(commitment),
                      sorted(aggregate_events,
                             key=lambda elem: elem.aggregate_version
                             ),
                      Commitment.shell())
