from dataclasses import dataclass
from datetime import date

from .period import Period


@dataclass()
class RepeatPeriod:
    start_date: date
    every: int
    period: Period

    def __post_init__(self):
        self.every = self.every or 1
