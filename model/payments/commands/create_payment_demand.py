from dataclasses import dataclass
from datetime import date

from model.commons.vo.correlation_id import CorrelationId
from model.commons.vo.money import Money
from model.payments.vo.purpose import Purpose
from model.payments.vo.transfer_recipient_data import TransferRecipientData


@dataclass(frozen=True)
class CreatePaymentDemand:
    money: Money
    payment_deadline: date
    purpose: Purpose
    correlation_id: CorrelationId
    transfer_recipient_data: TransferRecipientData
