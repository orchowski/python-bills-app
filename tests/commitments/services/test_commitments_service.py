from datetime import date
from decimal import Decimal

import pytest

from application.event_publisher import DefaultEventPublisher
from model.commitments.commands.add_commitment import AddCommitment
from model.commitments.commands.update_commitment import UpdateCommitment
from model.commitments.commitment import ActiveCommitment, InActiveCommitment
from model.commitments.events import CommitmentAddedEvent, CommitmentAmountChangedEvent, CommitmentDeactivatedEvent, \
    CommitmentActivatedEvent, CommitmentMetadataUpdatedEvent, CommitmentRepeatPeriodChangedEvent
from model.commitments.services.commitment_service import CommitmentService
from model.commitments.vo.commitment_id import CommitmentId
from model.commitments.vo.metadata import Metadata
from model.commitments.vo.period import Period
from model.commons.vo.context import WalletId, Context
from model.commons.vo.user_id import UserId
from tests.assertion_utils import assert_that_contains_same_event_types_in_order
from tests.commitments.mocks.commitment_repository import TestCommitmentRepository
from tests.common.app_test_config import ApplicationTestingFactory
from tests.common.mocks.registering_event_handler import RegisteringEventHandler

SUCCESSFUL_RESULT = 'successful result expected'

TEST_AMOUNT = Decimal(123)
TEST_UNIT = "EUR"
TEST_METADATA = Metadata("rent for house", "a description")
TEST_START_DATE = date(2021, 7, 20)
TEST_PERIOD = Period.MONTH
TEST_EVERY_PERIOD = 1
TEST_ACTIVITY = True


# TODO : fragile tests on events order. They should be event type-based instead of index
class TestCommitmentsService:
    registered_events: RegisteringEventHandler
    commitments_repo: TestCommitmentRepository

    @pytest.fixture(autouse=True)
    def setup(self):
        self.registered_events = RegisteringEventHandler()
        self.commitments_repo = TestCommitmentRepository(
            DefaultEventPublisher([self.registered_events]))
        yield CommitmentService(self.commitments_repo)

    def test_should_add_commitment_with_all_data(self, setup):
        # given
        commitment_service = setup

        # when
        _, result = commitment_service.add(create_add_commitment_command())
        events = self.registered_events.achieved_events

        # then
        assert result.succeded(), SUCCESSFUL_RESULT
        assert len(events) == 1, "should contain one event"

        event = events[0]
        assert isinstance(
            event, CommitmentAddedEvent), "should be type of commitmentAddedEvent"
        assert event.amount == TEST_AMOUNT
        assert event.unit.name == TEST_UNIT
        assert event.metadata == TEST_METADATA
        assert event.repeat_period.start_date == TEST_START_DATE
        assert event.repeat_period.period == TEST_PERIOD
        assert event.repeat_period.every == TEST_EVERY_PERIOD
        assert event.active == TEST_ACTIVITY

        commitment = self.commitments_repo.get_by(CommitmentId.of(event.aggregate_id))

        assert isinstance(
            commitment, ActiveCommitment), "result commitment should be type of ActiveCommitment"

    def test_should_add_commitment_when_inactive(self, setup):
        # given
        commitment_service = setup

        # when
        _, result = commitment_service.add(create_add_commitment_command(active=False))
        events = self.registered_events.achieved_events

        # then
        assert result.succeded(), SUCCESSFUL_RESULT
        assert len(events) == 1, "should contain one event"

        event = events[0]
        assert isinstance(
            event, CommitmentAddedEvent), "should be type of commitmentAddedEvent"
        assert not event.active

        commitment = self.commitments_repo.get_by(CommitmentId.of(event.aggregate_id))
        assert isinstance(
            commitment, InActiveCommitment), "result commitment should be type of InActiveCommitment"

    def test_update_with_same_data_should_regenerate_metadata(self, setup):
        # given
        commitment_service = setup

        # when
        commitment_service.add(create_add_commitment_command())
        commitment_id = CommitmentId.of(
            self.registered_events.achieved_events[0].aggregate_id)
        result = commitment_service.update(create_update_commitment_command(commitment_id))
        events = self.registered_events.achieved_events

        # then
        assert result.succeded(), SUCCESSFUL_RESULT
        assert_that_contains_same_event_types_in_order(
            events, [
                CommitmentAddedEvent, CommitmentMetadataUpdatedEvent
            ])

    def test_update_amount_should_publish_amount_changed_event(self, setup):
        # given
        commitment_service = setup
        new_amount = Decimal(444)

        # when
        commitment_service.add(create_add_commitment_command())
        commitment_id = CommitmentId.of(
            self.registered_events.achieved_events[0].aggregate_id)
        result = commitment_service.update(
            create_update_commitment_command(commitment_id, amount=new_amount))
        events = self.registered_events.achieved_events

        # then
        assert result.succeded(), SUCCESSFUL_RESULT
        assert_that_contains_same_event_types_in_order(
            events, [
                CommitmentAddedEvent, CommitmentMetadataUpdatedEvent, CommitmentAmountChangedEvent
            ])

        assert events[2].amount == new_amount, "amount changed event should contain new amount"

    def test_update_amount_unit_should_publish_amount_changed_event(self, setup):
        # given
        commitment_service = setup
        new_unit = "USD"

        # when
        commitment_service.add(create_add_commitment_command())
        commitment_id = CommitmentId.of(
            self.registered_events.achieved_events[0].aggregate_id)
        result = commitment_service.update(
            create_update_commitment_command(commitment_id, unit=new_unit))
        events = self.registered_events.achieved_events

        # then
        assert result.succeded(), SUCCESSFUL_RESULT
        assert_that_contains_same_event_types_in_order(
            events, [
                CommitmentAddedEvent, CommitmentMetadataUpdatedEvent, CommitmentAmountChangedEvent
            ])

        assert events[2].unit.name == new_unit, "amount changed event should contain new unit"

    def test_update_repeat_period_data_should_publish_repeat_period_changed_event(self, setup):
        # given
        commitment_service = setup
        new_commitmenting_period = Period.WEEK

        # when
        commitment_service.add(create_add_commitment_command())
        commitment_id = CommitmentId.of(
            self.registered_events.achieved_events[0].aggregate_id)
        result = commitment_service.update(create_update_commitment_command(
            commitment_id, repeat_period=new_commitmenting_period))
        events = self.registered_events.achieved_events

        # then
        assert result.succeded(), SUCCESSFUL_RESULT
        assert_that_contains_same_event_types_in_order(
            events, [
                CommitmentAddedEvent, CommitmentMetadataUpdatedEvent, CommitmentRepeatPeriodChangedEvent
            ])

        assert events[2].repeat_period.period == new_commitmenting_period

    def test_update_repeat_period_start_date_should_publish_repeat_period_changed_event(self, setup):
        # given
        commitment_service = setup
        new_start_date = date(2021, 7, 22)

        # when
        commitment_service.add(create_add_commitment_command())
        commitment_id = CommitmentId.of(
            self.registered_events.achieved_events[0].aggregate_id)
        result = commitment_service.update(create_update_commitment_command(
            commitment_id, start_date=new_start_date))
        events = self.registered_events.achieved_events

        # then
        assert result.succeded(), SUCCESSFUL_RESULT
        assert_that_contains_same_event_types_in_order(
            events, [
                CommitmentAddedEvent, CommitmentMetadataUpdatedEvent, CommitmentRepeatPeriodChangedEvent
            ])

        assert events[2].repeat_period.start_date == new_start_date

    def test_update_repeat_period_every_count_should_publish_repeat_period_changed_event(self, setup):
        # given
        commitment_service = setup
        new_every = date(2021, 7, 22)

        # when
        commitment_service.add(create_add_commitment_command())
        commitment_id = CommitmentId.of(
            self.registered_events.achieved_events[0].aggregate_id)
        result = commitment_service.update(
            create_update_commitment_command(commitment_id, every_period=new_every))
        events = self.registered_events.achieved_events

        # then
        assert result.succeded(), SUCCESSFUL_RESULT
        assert_that_contains_same_event_types_in_order(
            events, [
                CommitmentAddedEvent, CommitmentMetadataUpdatedEvent, CommitmentRepeatPeriodChangedEvent
            ])

        assert events[2].repeat_period.every == new_every

    def test_update_activity_should_change_commitment_type_and_publish_deactivated_event(self, setup):
        # given
        commitment_service = setup

        # when
        commitment_service.add(create_add_commitment_command())
        commitment_id = CommitmentId.of(
            self.registered_events.achieved_events[0].aggregate_id)
        result = commitment_service.update(
            create_update_commitment_command(commitment_id, active=False))
        events = self.registered_events.achieved_events

        # then
        assert result.succeded(), SUCCESSFUL_RESULT
        assert_that_contains_same_event_types_in_order(
            events, [
                CommitmentAddedEvent, CommitmentDeactivatedEvent, CommitmentMetadataUpdatedEvent
            ])
        commitment = self.commitments_repo.get_by(CommitmentId.of(events[0].aggregate_id))
        assert isinstance(
            commitment, InActiveCommitment), "result commitment should be type of InActivecommitment"

    def test_update_incactive_commitment_should_change_commitment_type_and_publish_activated_event(self, setup):
        # given
        commitment_service = setup
        new_every = date(2021, 7, 22)

        # when
        commitment_service.add(create_add_commitment_command(active=False))
        commitment_id = CommitmentId.of(
            self.registered_events.achieved_events[0].aggregate_id)
        result = commitment_service.update(
            create_update_commitment_command(commitment_id, active=True))
        events = self.registered_events.achieved_events

        # then
        assert result.succeded(), SUCCESSFUL_RESULT
        assert_that_contains_same_event_types_in_order(
            events, [
                CommitmentAddedEvent, CommitmentActivatedEvent, CommitmentMetadataUpdatedEvent
            ])
        commitment = self.commitments_repo.get_by(CommitmentId.of(events[0].aggregate_id))
        assert isinstance(
            commitment, ActiveCommitment), "result commitment should be type of Activecommitment"


def create_add_commitment_command(
        amount=TEST_AMOUNT,
        unit=TEST_UNIT,
        metadata=TEST_METADATA,
        start_date=TEST_START_DATE,
        repeat_period=TEST_PERIOD,
        every_period=TEST_EVERY_PERIOD,
        active=TEST_ACTIVITY
):
    return AddCommitment(
        amount=amount,
        unit=unit,
        metadata=metadata,
        start_date=start_date,
        repeat_period=repeat_period,
        every_period=every_period,
        active=active,
        context=Context(UserId('veryUniqueId'), WalletId())
    )


def create_update_commitment_command(
        commitment_id,
        amount=TEST_AMOUNT,
        unit=TEST_UNIT,
        metadata=TEST_METADATA,
        start_date=TEST_START_DATE,
        repeat_period=TEST_PERIOD,
        every_period=TEST_EVERY_PERIOD,
        active=TEST_ACTIVITY
):
    return UpdateCommitment(
        id=commitment_id,
        amount=amount,
        unit=unit,
        metadata=metadata,
        start_date=start_date,
        repeat_period=repeat_period,
        every_period=every_period,
        active=active,
        context=Context(UserId('veryUniqueId'), WalletId())
    )
