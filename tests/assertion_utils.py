import collections
from typing import List, Type

from model.commitments.events import DomainEvent


def assert_that_contains_same_event_types_in_order(result_events: List[DomainEvent], expected_events: List[Type]):
    assert len(result_events) == len(
        expected_events), f"Events assertion error. Expected: {len(expected_events)} but got :{len(result_events)}"
    for index, value in enumerate(result_events):
        assert expected_events[index] == type(
            value), f"{index}'d event should be type of: {expected_events[index]}, but got {type(value)}"


def assert_that_contains_same_event_types(result_events: List[DomainEvent], expected_events: List[Type]):
    assert len(result_events) == len(
        expected_events), f"Events assertion error. Expected: {len(expected_events)} but got :{len(result_events)}"
    result_groups = collections.Counter([type(x) for x in result_events])
    expected_groups = collections.Counter(expected_events)
    assert result_groups == expected_groups
