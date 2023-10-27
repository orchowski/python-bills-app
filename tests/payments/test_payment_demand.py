from datetime import date
from decimal import Decimal

from model.commons.aggregate_root import AggregateId
from model.commons.vo.correlation_id import CorrelationId
from model.commons.vo.money import Money
from model.commons.vo.unit import Unit
from model.payments.commands.create_payment_demand import CreatePaymentDemand
from model.payments.commands.satisfy_payment_demand import SatisfyPaymentDemand
from model.payments.payment_demand import PaymentDemand
from model.payments.payment_demand_events import PaymentDemandInitiatedEvent, PaymentDemandSatisfyRequestedEvent
from model.payments.policies.transfer_title_policies import StaticTitlePolicy
from model.payments.vo.payment_demand_id import PaymentDemandId
from model.payments.vo.purpose import PaymentCategory, Purpose
from model.payments.vo.title_format import TitleFormat, TitleFormatTypes
from model.payments.vo.transfer_recipient_data import TransferRecipientData
from tests.assertion_utils import assert_that_contains_same_event_types_in_order

TEST_AMOUNT = Money(Decimal(123), Unit('USD'))
TEST_DEADLINE = date(2021, 7, 24)
TEST_PURPOSE = Purpose("some description", PaymentCategory("cat_id"))
TEST_CORRELATION_ID = CorrelationId(AggregateId.generate_new(), "COMMITMENT")
TEST_TRANSFER_RECIPIENT_DATA = TransferRecipientData('1', 'roman z koszalina', '123123123123123123123')
TEST_TITLE_FORMAT = TitleFormat('test transfer title', TitleFormatTypes.STATIC)


class TestPaymentDemand:

    def test_payment_demand_should_be_created_with_created_event(self):
        # GIVEN
        command = self.default_create_command()

        # WHEN
        result = PaymentDemand.create_from_payment_demand_command(command)

        # THEN
        events = result.extract_events_with_state_clearing()

        assert_that_contains_same_event_types_in_order(
            events, [PaymentDemandInitiatedEvent]
        )
        assert isinstance(
            result, PaymentDemand), f'expected {PaymentDemand.__name__} of aggregate'

    def test_payment_demand_should_be_satisfied(self):
        # GIVEN
        demand = PaymentDemand.create_from_payment_demand_command(self.default_create_command())
        command = self.default_satisfy_command(demand.id)

        # WHEN
        result, _ = demand.satisfy(StaticTitlePolicy(command.title_format.format))

        # THEN
        if result is None:
            assert False, 'aggregate should not be none'
        events = result.extract_events_with_state_clearing()

        assert_that_contains_same_event_types_in_order(
            events, [PaymentDemandInitiatedEvent, PaymentDemandSatisfyRequestedEvent]
        )

    def default_create_command(self):
        return CreatePaymentDemand(
            money=TEST_AMOUNT,
            payment_deadline=TEST_DEADLINE,
            purpose=TEST_PURPOSE,
            correlation_id=TEST_CORRELATION_ID,
            transfer_recipient_data=TEST_TRANSFER_RECIPIENT_DATA
        )

    def default_satisfy_command(self, id: AggregateId):
        return SatisfyPaymentDemand(
            payment_demand_id=PaymentDemandId.of(id),
            title_format=TEST_TITLE_FORMAT
        )
