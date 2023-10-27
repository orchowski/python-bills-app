from abc import abstractmethod
from typing import Optional

from model.commons.aggregate_store import AggregateStore
from model.commons.result import Result, Success
from model.payments.payment import Payment
from model.payments.vo.payment_id import PaymentId


class PaymentStore(AggregateStore):

    @abstractmethod
    def save(self, payment: Payment) -> Result:
        super().save(payment)
        if not isinstance(payment, Payment):
            raise TypeError("payment should be type of Payment")
        return Success()

    @abstractmethod
    def get_by(self, payment_id: PaymentId) -> Optional[Payment]:
        if not isinstance(payment_id, PaymentId):
            raise TypeError("id should be type of PaymentId")
        return None
