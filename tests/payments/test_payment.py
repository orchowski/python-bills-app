from datetime import date
from decimal import Decimal

from model.commons.aggregate_root import AggregateId
from model.commons.vo.correlation_id import CorrelationId
from model.commons.vo.money import Money
from model.commons.vo.unit import Unit
from model.payments.commands.payment_requested_command import PaymentRequestedCommand
from model.payments.payment import Payment, FinishedPayment
from model.payments.payment_events import PaymentCompletedEvent, PaymentInitiatedEvent
from model.payments.vo.purpose import PaymentCategory, Purpose
from model.payments.vo.transfer_recipient_data import TransferRecipientData
from tests.assertion_utils import assert_that_contains_same_event_types_in_order

TEST_AMOUNT = Money(Decimal(123), Unit('USD'))
TEST_DEADLINE = date(2021, 7, 24)
TEST_PURPOSE = Purpose("some description", PaymentCategory("cat_id"))
TEST_CORRELATION_ID = CorrelationId(AggregateId.generate_new(), "COMMITMENT")
TEST_TRANSFER_RECIPIENT_DATA = TransferRecipientData('1', 'roman z koszalina', '123123123123123123123')
TEST_PAYMENT_TITLE = "Example payment title"


# @pytest.mark.skip(reason="feature in progress, TDD - test in red stage")
def test_payment_should_be_created_with_initiated_event():
    # GIVEN
    command = create_default_payment_requested()

    # WHEN
    result = Payment.create_from_payment_requested_command(command)

    # THEN
    events = result.extract_events_with_state_clearing()
    assert len(
        events) == 1, f'should contain only one event, but got {len(events)}'
    assert isinstance(
        events[0], PaymentInitiatedEvent), f'expected {PaymentInitiatedEvent.__name__}'
    assert isinstance(
        result, Payment), f'expected {Payment.__name__} of aggregate'


def test_payment_should_emit_completed_event_on_completion():
    # GIVEN
    command = create_default_payment_requested()
    payment = Payment.create_from_payment_requested_command(command)
    # WHEN
    result = payment.complete()

    # THEN
    events = result[0].extract_events_with_state_clearing()

    assert_that_contains_same_event_types_in_order(
        events, [PaymentInitiatedEvent, PaymentCompletedEvent]
    )
    assert isinstance(
        result[0], FinishedPayment), f'expected {FinishedPayment.__name__} of aggregate'


def test_shouldnt_allow_to_complete_twice():
    # GIVEN
    command = create_default_payment_requested()
    payment = Payment.create_from_payment_requested_command(command)
    # WHEN
    result = payment.complete()[0].complete()

    # THEN
    assert isinstance(
        result[0], FinishedPayment), f'expected {FinishedPayment.__name__} of aggregate'

    assert not result[1].succeded()


def create_default_payment_requested() -> PaymentRequestedCommand:
    return PaymentRequestedCommand(
        payment_title=TEST_PAYMENT_TITLE,
        money=TEST_AMOUNT,
        correlation_id=TEST_CORRELATION_ID,
        transfer_recipient_data=TEST_TRANSFER_RECIPIENT_DATA
    )
