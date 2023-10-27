from dataclasses import dataclass

from model.commons.vo.correlation_id import CorrelationId
from model.commons.vo.money import Money
from model.payments.vo.transfer_recipient_data import TransferRecipientData


@dataclass(frozen=True)
class PaymentRequestedCommand:
    payment_title: str
    money: Money
    correlation_id: CorrelationId
    transfer_recipient_data: TransferRecipientData
