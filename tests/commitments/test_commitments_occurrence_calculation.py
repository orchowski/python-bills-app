from datetime import date
from typing import List

from model.commitments.services.params.commitments_calculation_data import CyclicCommitmentDefinition, \
    SingleCommitmentDefinition, OccurrenceRange
from model.commitments.vo.period import Period
from model.commitments.vo.repeat_period import RepeatPeriod

COMMITMENT_ID = "12312312323"


def test_single_commitment_definition_is_returned_when_in_range():
    # given
    deadline = date(2020, 3, 1)
    commitment = SingleCommitmentDefinition(COMMITMENT_ID, deadline)
    a_range = OccurrenceRange(after=date(2020, 2, 24), before=date(2020, 3, 5))

    # when
    occurrences = commitment.occurrences_in(a_range)

    # then
    assert len(list(occurrences.keys())) == 1, "should have only one commitment"
    commitment, dates = occurrences.popitem()
    assert commitment.a_id == COMMITMENT_ID, "should have original commitment id"
    assert len(dates) == 1, "should have one occurrence"
    assert dates[0] == deadline, "should occur on deadline"


def test_single_commitment_definition_is_returned_when_hit_after_date():
    # given
    deadline = date(2020, 3, 1)
    commitment = SingleCommitmentDefinition(COMMITMENT_ID, deadline)
    a_range = OccurrenceRange(after=date(2020, 3, 1), before=date(2020, 3, 5))

    # when
    occurrences = commitment.occurrences_in(a_range)

    # then
    assert len(list(occurrences.keys())) == 1, "should have only one commitment"
    commitment, dates = occurrences.popitem()
    assert commitment.a_id == COMMITMENT_ID, "should have original commitment id"
    assert len(dates) == 1, "should have one occurrence"
    assert dates[0] == deadline, "should occur on deadline"


def test_single_commitment_definition_is_returned_when_hit_before_date():
    # given
    deadline = date(2020, 3, 1)
    commitment = SingleCommitmentDefinition(COMMITMENT_ID, deadline)
    a_range = OccurrenceRange(after=date(2020, 2, 1), before=date(2020, 3, 1))

    # when
    occurrences = commitment.occurrences_in(a_range)

    # then
    assert len(list(occurrences.keys())) == 1, "should have only one commitment"
    commitment, dates = occurrences.popitem()
    assert commitment.a_id == COMMITMENT_ID, "should have original commitment id"
    assert len(dates) == 1, "should have one occurrence"
    assert dates[0] == deadline, "should occur on deadline"


def test_daily_cyclic_commitment_definition_once_in_range_after_start_date():
    start_date = date(2020, 3, 1)
    cyclic_commitment_definition_in_range(
        repeat_period=RepeatPeriod(start_date=start_date,
                                   every=2,
                                   period=Period.DAY
                                   ),
        a_range=OccurrenceRange(
            after=date(2020, 3, 20),
            before=date(2020, 3, 21)
        ),
        expected_occurrence_date=[date(2020, 3, 21)]
    )


def test_daily_cyclic_commitment_definition_once_in_range_before_start_date():
    start_date = date(2020, 3, 1)
    cyclic_commitment_definition_in_range(
        repeat_period=RepeatPeriod(start_date=start_date,
                                   every=2,
                                   period=Period.DAY
                                   ),
        a_range=OccurrenceRange(
            after=date(2020, 2, 20),
            before=date(2020, 3, 1)
        ),
        expected_occurrence_date=[date(2020, 3, 1)]
    )


def test_daily_cyclic_commitment_definition_in_wide_range():
    start_date = date(2020, 12, 30)
    cyclic_commitment_definition_in_range(
        repeat_period=RepeatPeriod(start_date=start_date,
                                   every=4,
                                   period=Period.DAY
                                   ),
        a_range=OccurrenceRange(
            after=date(2020, 12, 15),
            before=date(2021, 1, 12)
        ),
        expected_occurrence_date=[date(2020, 12, 30),
                                  date(2021, 1, 3),
                                  date(2021, 1, 7),
                                  date(2021, 1, 11)
                                  ],
        occurrences_number=4
    )


def test_weekly_cyclic_commitment_definition_once_in_range_after_start_date():
    start_date = date(2020, 3, 1)  # sunday
    cyclic_commitment_definition_in_range(
        repeat_period=RepeatPeriod(start_date=start_date,
                                   every=1,
                                   period=Period.WEEK
                                   ),
        a_range=OccurrenceRange(
            after=date(2021, 2, 1),
            before=date(2021, 2, 12)
        ),
        expected_occurrence_date=[
            date(2021, 2, 7)
        ]
    )


def test_weekly_cyclic_commitment_definition_once_in_range_before_start_date():
    start_date = date(2020, 3, 1)  # sunday
    cyclic_commitment_definition_in_range(
        repeat_period=RepeatPeriod(start_date=start_date,
                                   every=1,
                                   period=Period.WEEK
                                   ),
        a_range=OccurrenceRange(
            after=date(2021, 3, 1),
            before=date(2021, 3, 12)
        ),
        expected_occurrence_date=[
            date(2021, 3, 7)
        ]
    )


def test_weekly_cyclic_commitment_definition_in_wide_range_after_start_date():
    start_date = date(2020, 3, 1)  # sunday
    cyclic_commitment_definition_in_range(
        repeat_period=RepeatPeriod(start_date=start_date,
                                   every=1,
                                   period=Period.WEEK
                                   ),
        a_range=OccurrenceRange(
            after=date(2021, 2, 1),
            before=date(2021, 2, 25)
        ),
        expected_occurrence_date=[
            date(2021, 2, 7),
            date(2021, 2, 14),
            date(2021, 2, 21),
        ],
        occurrences_number=3
    )


def test_weekly_cyclic_commitment_definition_in_wide_range_after_start_date_every2():
    start_date = date(2020, 3, 8)  # sunday
    cyclic_commitment_definition_in_range(
        repeat_period=RepeatPeriod(start_date=start_date,
                                   every=2,
                                   period=Period.WEEK
                                   ),
        a_range=OccurrenceRange(
            after=date(2021, 3, 1),
            before=date(2021, 4, 1)
        ),
        expected_occurrence_date=[
            date(2021, 3, 7),
            date(2021, 3, 21),
        ],
        occurrences_number=2
    )


def test_monthly_cyclic_commitment_definition_once_in_range_after_start_date():
    start_date = date(2020, 3, 1)  # sunday
    cyclic_commitment_definition_in_range(
        repeat_period=RepeatPeriod(start_date=start_date,
                                   every=1,
                                   period=Period.MONTH
                                   ),
        a_range=OccurrenceRange(
            after=date(2021, 2, 1),
            before=date(2021, 2, 12)
        ),
        expected_occurrence_date=[
            date(2021, 2, 1)
        ]
    )


def test_monthly_cyclic_commitment_definition_once_in_range_before_start_date():
    start_date = date(2020, 3, 1)
    cyclic_commitment_definition_in_range(
        repeat_period=RepeatPeriod(start_date=start_date,
                                   every=1,
                                   period=Period.MONTH
                                   ),
        a_range=OccurrenceRange(
            after=date(2020, 2, 1),
            before=date(2020, 3, 12)
        ),
        expected_occurrence_date=[
            date(2020, 3, 1)
        ]
    )


def test_monthly_cyclic_commitment_definition_once_in_wide_range():
    start_date = date(2020, 3, 14)
    cyclic_commitment_definition_in_range(
        repeat_period=RepeatPeriod(start_date=start_date,
                                   every=1,
                                   period=Period.MONTH
                                   ),
        a_range=OccurrenceRange(
            after=date(2021, 2, 1),
            before=date(2021, 6, 12)
        ),
        expected_occurrence_date=[
            date(2021, 2, 14),
            date(2021, 3, 14),
            date(2021, 4, 14),
            date(2021, 5, 14)
        ],
        occurrences_number=4
    )


def test_monthly_cyclic_commitment_definition_once_in_wide_range_every_2():
    start_date = date(2021, 2, 14)
    cyclic_commitment_definition_in_range(
        repeat_period=RepeatPeriod(start_date=start_date,
                                   every=2,
                                   period=Period.MONTH
                                   ),
        a_range=OccurrenceRange(
            after=date(2021, 2, 15),
            before=date(2021, 6, 14)
        ),
        expected_occurrence_date=[
            date(2021, 4, 14),
            date(2021, 6, 14)
        ],
        occurrences_number=2
    )


def cyclic_commitment_definition_in_range(repeat_period: RepeatPeriod,
                                       a_range: OccurrenceRange,
                                       expected_occurrence_date: List[date],
                                       occurrences_number: int = 1):
    # given
    commitment = CyclicCommitmentDefinition(COMMITMENT_ID,
                                            repeat_period)

    # when
    occurrences = commitment.occurrences_in(a_range)

    # then
    assert len(list(occurrences.keys())) == 1, f"should have only one commitment"
    commitment, dates = occurrences.popitem()
    assert commitment.a_id == COMMITMENT_ID, "should have original commitment id"
    assert len(dates) == occurrences_number, f"should have {occurrences_number} occurrences_of_given_in_range"
    assert dates == expected_occurrence_date, f"should occur on {expected_occurrence_date}"
