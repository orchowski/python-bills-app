from functools import reduce
from typing import Set

import infrastructure.logger as logger
from model.commons.aggregate_root import DomainEvent
from model.commons.result import Result, Success, Fail
from model.payments.payment_demand import PaymentDemand
from model.payments.stores.payment_demand_store import PaymentDemandStore
from model.payments.vo.payment_demand_id import PaymentDemandId


class PaymentDemandRepository(PaymentDemandStore):
    __events: Set[DomainEvent] = set()

    def save(self, demand: PaymentDemand) -> Result:
        try:
            super(PaymentDemandRepository, self).save(demand)
            new_events = demand.extract_events_with_state_clearing()
            if len(set(new_events).difference(self.__events)) != len(new_events):
                return Fail("duplicated event for aggregate occured, transaction failed")
            self.__events.update(new_events)
            self.publish_all(new_events)
        except Exception as e:
            logger.error('Test payment_demand repo saving error %s', e)
            return Fail(e)
        return Success()

    def get_by(self, demand_id: PaymentDemandId) -> PaymentDemand:
        super(PaymentDemandRepository, self).get_by(demand_id)
        aggregate_events = list(
            filter(lambda event: event.aggregate_id == demand_id, self.__events))
        return reduce(lambda demand, event: event.apply(demand),
                      sorted(aggregate_events,
                             key=lambda elem: elem.aggregate_version
                             ),
                      PaymentDemand.shell())
