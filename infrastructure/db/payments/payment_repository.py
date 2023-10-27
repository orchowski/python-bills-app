from functools import reduce
from typing import Set

import infrastructure.logger as logger
from model.commons.aggregate_root import DomainEvent
from model.commons.result import Result, Success, Fail
from model.payments.payment import Payment
from model.payments.stores.payment_store import PaymentStore
from model.payments.vo.payment_id import PaymentId


class PaymentRepository(PaymentStore):
    __events: Set[DomainEvent] = set()

    def save(self, demand: Payment) -> Result:
        try:
            super(PaymentRepository, self).save(demand)
            new_events = demand.extract_events_with_state_clearing()
            if len(set(new_events).difference(self.__events)) != len(new_events):
                return Fail("duplicated event for aggregate occured, transaction failed")
            self.__events.update(new_events)
            self.publish_all(new_events)
        except Exception as e:
            logger.error('Test payment repo saving error %s', e)
            return Fail(e)
        return Success()

    def get_by(self, demand_id: PaymentId) -> Payment:
        super(PaymentRepository, self).get_by(demand_id)
        aggregate_events = list(
            filter(lambda event: event.aggregate_id == demand_id, self.__events))
        return reduce(lambda demand, event: event.apply(demand),
                      sorted(aggregate_events,
                             key=lambda elem: elem.aggregate_version
                             ),
                      Payment.shell())
