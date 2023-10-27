from functools import reduce
from typing import Set

import infrastructure.logger as logger
from model.commitments.commitment import Commitment
from model.commitments.stores.commitment_store import CommitmentStore
from model.commitments.vo.commitment_id import CommitmentId
from model.commons.aggregate_root import DomainEvent
from model.commons.result import Fail, Result, Success


class CommitmentRepository(CommitmentStore):
    __events: Set[DomainEvent] = set()

    def save(self, commitment: Commitment) -> Result:
        try:
            super(CommitmentRepository, self).save(commitment)
            new_events = commitment.extract_events_with_state_clearing()
            if len(set(new_events).difference(self.__events)) != len(new_events):
                return Fail("duplicated event for aggregate occurred, transaction failed")
            self.__events.update(new_events)
            self.publish_all(new_events)
        except Exception as e:
            logger.error('Test commitment repo saving error %s', e)
            return Fail(e)
        return Success()

    def get_by(self, id: CommitmentId) -> Commitment:
        super(CommitmentRepository, self).get_by(id)
        aggregate_events = list(
            filter(lambda event: event.aggregate_id == id, self.__events))
        return reduce(lambda commitment, event: event.apply(commitment),
                      sorted(aggregate_events,
                             key=lambda elem: elem.aggregate_version
                             ),
                      Commitment.shell())
