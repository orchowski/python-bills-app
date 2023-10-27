from abc import abstractmethod
from typing import Optional

from model.commons.aggregate_store import AggregateStore
from model.commons.result import Result, Success
from model.payments.payment_demand import PaymentDemand
from model.payments.vo.payment_demand_id import PaymentDemandId


class PaymentDemandStore(AggregateStore):

    @abstractmethod
    def save(self, payment_demand: PaymentDemand) -> Result:
        super().save(payment_demand)
        if not isinstance(payment_demand, PaymentDemand):
            raise TypeError("payment_demand should be type of PaymentDemand")
        return Success()

    @abstractmethod
    def get_by(self, payment_demand_id: PaymentDemandId) -> Optional[PaymentDemand]:
        if not isinstance(payment_demand_id, PaymentDemandId):
            raise TypeError("payment_demand_id should be type of PaymentDemandId")
        return None
