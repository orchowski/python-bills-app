from __future__ import annotations

from abc import ABC, abstractmethod
from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Dict

from dateutil.relativedelta import relativedelta

from model.commitments.vo.period import Period
from model.commitments.vo.repeat_period import RepeatPeriod


def diff_month(d1, d2) -> int:
    return (d1.year - d2.year) * 12 + d1.month - d2.month


def add_months(source_date, months) -> date:
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, monthrange(year, month)[1])
    return date(year, month, day)


@dataclass()
class OccurrenceRange:
    __after: date
    __before: date

    def __init__(self, after: date, before: date):

        if after is None:
            raise ValueError("after can't be None")
        if before is None:
            raise ValueError("before can't be None")
        if after >= before:
            raise ValueError("before have to be greater after")

        self.__after = after
        self.__before = before

    @property
    def after(self) -> date:
        return self.__after

    @property
    def before(self) -> date:
        return self.__before


class CommitmentDefinition(ABC):
    __commitment_id: str

    def __init__(self, commitment_id: str):
        if commitment_id is None:
            raise ValueError("__commitment_id can't be None")
        self.__commitment_id = commitment_id

    @property
    def a_id(self):
        return self.__commitment_id

    @abstractmethod
    def occurrences_in(self, range: OccurrenceRange) -> Dict[CommitmentDefinition, List[date]]:
        return {}

    def __eq__(self, other):
        return self.a_id == other.a_id

    def __hash__(self):
        return hash(self.a_id)


class SingleCommitmentDefinition(CommitmentDefinition):
    __deadline: date

    @property
    def deadline(self) -> date:
        return self.__deadline

    def __init__(self, commitment_id: str, deadline: date):
        super().__init__(commitment_id)
        if deadline is None:
            raise ValueError("to_date can't be None")
        self.__deadline = deadline

    def occurrences_in(self, a_range: OccurrenceRange) -> Dict[CommitmentDefinition, List[date]]:
        if a_range.after <= self.deadline <= a_range.before:
            return {self: [self.deadline]}
        return super(SingleCommitmentDefinition, self).occurrences_in(a_range)


class _Cycle(ABC):
    _amount: float
    _every: int
    _repeat_period: RepeatPeriod

    @abstractmethod
    def __init__(self, repeat_period: RepeatPeriod, amount: float, every: int):
        self._repeat_period = repeat_period
        self._amount = amount
        self._every = every

    @classmethod
    def of(cls, repeat_period: RepeatPeriod, to: date) -> _Cycle:
        if repeat_period.period == Period.DAY:
            return _DayCycle.of(repeat_period, to)
        if repeat_period.period == Period.WEEK:
            return _WeekCycle.of(repeat_period, to)
        if repeat_period.period == Period.MONTH:
            return _MonthCycle.of(repeat_period, to)
        raise AttributeError(f"Period not supported: {repeat_period.period}")

    @abstractmethod
    def a_date(self) -> date:
        pass

    @abstractmethod
    def next(self) -> _Cycle:
        pass


class _DayCycle(_Cycle):

    def __init__(self, repeat_period: RepeatPeriod, amount: float, every: int):
        _Cycle.__init__(self, repeat_period, amount, every)

    def amount(self) -> float:
        return self._amount

    @classmethod
    def of(cls, repeat_period: RepeatPeriod, to: date) -> _Cycle:
        delta = repeat_period.start_date - to
        amount = delta.days / repeat_period.every
        return cls(repeat_period, abs(amount) if amount < 0 else 0, repeat_period.every)

    def a_date(self) -> date:
        return self._repeat_period.start_date + timedelta(days=int(self._amount) * self._every)

    def next(self) -> _Cycle:
        return _DayCycle(self._repeat_period, self._amount + 1, self._every)


class _WeekCycle(_Cycle):
    def __init__(self, repeat_period: RepeatPeriod, amount: float, every: int):
        _Cycle.__init__(self, repeat_period, amount, every)

    def amount(self) -> float:
        return self._amount

    @classmethod
    def of(cls, repeat_period: RepeatPeriod, to: date) -> _Cycle:
        delta = repeat_period.start_date - to
        amount = delta.days / 7 / repeat_period.every
        return cls(repeat_period, abs(amount) if amount < 0 else 0, repeat_period.every)

    def a_date(self) -> date:
        return self._repeat_period.start_date + timedelta(days=int(self._amount) * self._every * 7)

    def next(self) -> _Cycle:
        return _WeekCycle(self._repeat_period, self._amount + 1, self._every)


class _MonthCycle(_Cycle):
    def __init__(self, repeat_period: RepeatPeriod, amount: float, every: int):
        _Cycle.__init__(self, repeat_period, amount, every)

    def amount(self) -> float:
        return self._amount

    @classmethod
    def of(cls, repeat_period: RepeatPeriod, to: date) -> _Cycle:
        delta = diff_month(repeat_period.start_date, to) / repeat_period.every
        return cls(repeat_period, abs(delta) if delta < 0 else 0, repeat_period.every)

    def a_date(self) -> date:
        return self._repeat_period.start_date + relativedelta(months=int(self._amount) * self._every)

    def next(self) -> _Cycle:
        return _MonthCycle(self._repeat_period, self._amount + 1, self._every)


class CyclicCommitmentDefinition(CommitmentDefinition):
    __repeat_period: RepeatPeriod

    @property
    def repeat_period(self) -> RepeatPeriod:
        return self.__repeat_period

    def __init__(self, commitment_id: str, repeat_period: RepeatPeriod):
        super().__init__(commitment_id)
        if repeat_period is None:
            raise ValueError("repeat_period can't be None")
        self.__repeat_period = repeat_period

    def __str__(self) -> str:
        return self.a_id

    def occurrences_in(self, o_range: OccurrenceRange) -> Dict[CommitmentDefinition, List[date]]:
        def occurrence_dates():
            cycle = _Cycle.of(self.repeat_period, o_range.after)
            while cycle.a_date() <= o_range.before:
                if o_range.after <= cycle.a_date():
                    yield cycle.a_date()
                cycle = cycle.next()

        return {self: list(occurrence_dates())}

    @classmethod
    def create(cls, id: str, repeat_period: RepeatPeriod) -> CommitmentDefinition:
        return cls(id, repeat_period)
