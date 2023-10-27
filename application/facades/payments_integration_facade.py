from uuid import UUID

from model.commons.result import Result
from model.payments.commands.satisfy_payment_demand import SatisfyPaymentDemand
from model.payments.services.payments_service import PaymentService
from model.payments.vo.payment_demand_id import PaymentDemandId
from model.payments.vo.title_format import TitleFormat, TitleFormatTypes


class PaymentsIntegrationFacade:
    def __init__(self, payment_service: PaymentService):
        self.__payment_service = payment_service

    def run_payment(self, demand_id: str, transfer_title: str) -> Result:
        _, result = self.__payment_service.run_payment_process(SatisfyPaymentDemand(
            PaymentDemandId(UUID(demand_id)), TitleFormat(transfer_title, TitleFormatTypes.STATIC)
        ))
        return result
