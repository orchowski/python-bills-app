from typing import Tuple, Optional

from model.commons.result import Result, Fail, Success
from model.payments.commands.create_payment_demand import CreatePaymentDemand
from model.payments.commands.payment_requested_command import PaymentRequestedCommand
from model.payments.commands.satisfy_payment_demand import SatisfyPaymentDemand
from model.payments.payment import Payment
from model.payments.payment_demand import PaymentDemand
from model.payments.policies.transfer_title_policies import StaticTitlePolicy, TransferTitleGenerationPolicy
from model.payments.stores.bank_transfer_recipients_rm_store import BankTransferRecipientsRMStore
from model.payments.stores.payment_demand_store import PaymentDemandStore
from model.payments.stores.payment_store import PaymentStore
from model.payments.vo.payment_data import PaymentData
from model.payments.vo.payment_demand_id import PaymentDemandId
from model.payments.vo.payment_id import PaymentId
from model.payments.vo.title_format import TitleFormat, TitleFormatTypes


class PaymentService:
    __recipients_rm_store: BankTransferRecipientsRMStore
    __payment_demand_store: PaymentDemandStore
    __payment_store: PaymentStore

    def __init__(self,
                 recipients_rm_store: BankTransferRecipientsRMStore,
                 payment_demand_store: PaymentDemandStore,
                 payment_store: PaymentStore
                 ):
        self.__recipients_rm_store = recipients_rm_store
        self.__payment_demand_store = payment_demand_store
        self.__payment_store = payment_store

    def pay_for(self, payment_data: PaymentData) -> Tuple[Optional[PaymentDemandId], Result]:
        transfer_recipient_data = self.__recipients_rm_store.get_by_id(
            payment_data.recipient_id)
        if transfer_recipient_data is None:
            return None, Fail("no transfer data for given recipient")

        demand = PaymentDemand.create_from_payment_demand_command(
            CreatePaymentDemand(
                money=payment_data.money,
                payment_deadline=payment_data.payment_deadline,
                purpose=payment_data.purpose,
                correlation_id=payment_data.correlation_id,
                transfer_recipient_data=transfer_recipient_data
            )
        )
        return PaymentDemandId.of(demand.id), self.__payment_demand_store.save(demand)

    def run_payment_process(self, command: SatisfyPaymentDemand) -> Tuple[Optional[PaymentDemandId], Result]:
        def payment_demand_from_store() -> Optional[PaymentDemand]:
            return self.__payment_demand_store.get_by(
                command.payment_demand_id)

        def satisfy_demand_with(
                title_policy, demand):
            return demand.satisfy(title_policy)

        def save_satisfied_demand(satisfied_demand):
            return (
                satisfied_demand.id, self.__payment_demand_store.save(satisfied_demand))

        title_policy, result = self.__create_title_policy(command.title_format)
        if title_policy is None:
            return None, result

        demand = payment_demand_from_store()
        if not demand:
            return None, Fail("demand not found")

        demand, satisfy_result = satisfy_demand_with(title_policy, demand)
        if satisfy_result.failed():
            return None, satisfy_result

        demand_id, save_result = save_satisfied_demand(demand)
        if save_result.failed():
            return None, save_result

        return PaymentDemandId.of(demand_id), save_result

    def create_payment(self, command: PaymentRequestedCommand):
        self.__payment_store.save(
            Payment.create_from_payment_requested_command(
                command
            )
        )

    def complete_payment(self, id: PaymentId) -> Result:
        payment = self.__payment_store.get_by(id)
        if not payment:
            return Fail(f"payment {id} not found")

        payment, result = payment.complete()

        if result.failed():
            return result

        return self.__payment_store.save(payment)

    def __create_title_policy(self, title_format: TitleFormat) -> Tuple[
        Optional[TransferTitleGenerationPolicy], Result]:
        if title_format.type is TitleFormatTypes.STATIC:
            return StaticTitlePolicy(title_format.format), Success()
        else:
            return None, Fail("format type is not provided")
