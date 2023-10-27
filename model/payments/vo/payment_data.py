from dataclasses import dataclass
from datetime import date

from model.commons.vo.correlation_id import CorrelationId
from model.commons.vo.money import Money
from model.payments.vo.purpose import Purpose


@dataclass(frozen=True)
class PaymentData:
    money: Money
    payment_deadline: date
    purpose: Purpose
    correlation_id: CorrelationId
    recipient_id: str
