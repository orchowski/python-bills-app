from datetime import date
from decimal import Decimal

from model.commitments.commands.add_commitment import AddCommitment
from model.commitments.services.params.commitments_calculation_data import OccurrenceRange, CyclicCommitmentDefinition
from model.commitments.vo.metadata import Metadata
from model.commitments.vo.period import Period
from model.commitments.vo.repeat_period import RepeatPeriod
from model.commons.vo.context import WalletId, Context
from model.commons.vo.money import Money, Unit
from model.commons.vo.user_id import UserId
from tests.common.app_test_config import ApplicationTestingFactory

TEST_AMOUNT = Decimal(123)
TEST_UNIT = "EUR"
TEST_METADATA = Metadata("rent for house", "a description")
TEST_START_DATE = date(2021, 7, 1)
TEST_PERIOD = Period.MONTH
TEST_EVERY_PERIOD = 1
TEST_ACTIVITY = True
CONTEXT = Context(UserId("the_user123"), WalletId())
MONEY = Money(Decimal(123), Unit("USD"))
app = ApplicationTestingFactory()


def test_calculates_commitment_occurrences_for_all_commitments_in_repo():
    # GIVEN
    commitments_ids = [
        app.commitment_integration_facade.add_new_commitment(
            create_add_commitment_command(start_date=TEST_START_DATE, repeat_period=Period.MONTH)
        ),
        app.commitment_integration_facade.add_new_commitment(
            create_add_commitment_command(start_date=TEST_START_DATE, repeat_period=Period.MONTH, active=False)
        ),
        app.commitment_integration_facade.add_new_commitment(
            create_add_commitment_command(start_date=TEST_START_DATE, repeat_period=Period.DAY, every_period=15)
        ),
        app.commitment_integration_facade.add_new_commitment(
            create_add_commitment_command(start_date=date(2021, 2, 1), repeat_period=Period.MONTH)
        ),
        app.commitment_integration_facade.add_new_commitment(
            create_add_commitment_command(start_date=date(2022, 1, 1), repeat_period=Period.WEEK)
        )
    ]

    # WHEN
    result = app.commitments_in_period_service.occurrences_in_range(CONTEXT, OccurrenceRange(
        after=date(2021, 8, 10),
        before=date(2021, 12, 29)
    ))

    # THEN
    assert len(
        app.commitments_read_model_repo.commitments) == 5, 'five commitments added to read-model - can fail if async!'
    assert get_number_of_occurrences_for_index(commitments_ids, result, 0) == 4
    assert get_number_of_occurrences_for_index(commitments_ids, result, 1) == 0
    assert get_number_of_occurrences_for_index(commitments_ids, result, 2) == 10
    assert get_number_of_occurrences_for_index(commitments_ids, result, 3) == 4
    assert get_number_of_occurrences_for_index(commitments_ids, result, 4) == 0


def get_number_of_occurrences_for_index(commitments_ids, result, index):
    return len(
        result.get(CyclicCommitmentDefinition(str(commitments_ids[index][0]), RepeatPeriod(start_date=date(2021, 1, 1),
                                                                                        every=1,
                                                                                        period=Period.MONTH
                                                                                        )
                                              )
                   ) or []
    )


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
