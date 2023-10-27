from dataclasses import dataclass

from model.payments.vo.payment_demand_id import PaymentDemandId
from model.payments.vo.title_format import TitleFormat


@dataclass(frozen=True)
class SatisfyPaymentDemand:
    payment_demand_id: PaymentDemandId
    title_format: TitleFormat
