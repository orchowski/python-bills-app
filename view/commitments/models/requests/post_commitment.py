from datetime import date
from decimal import Decimal

from pydantic import BaseModel, condecimal, validator, constr

from model.commitments.vo.period import Period
from model.commons.time import current_date


class CreateCommitment(BaseModel):
    amount: condecimal(gt=0)
    unit: constr(strip_whitespace=True, min_length=3)
    title: str
    repeat_period: Period
    description: str = ""
    start_date: date = current_date()
    every_period: int = 1
    active: bool = True

    @validator("start_date", pre=True)
    def parse_start_date(cls, value):
        return date.fromisoformat(value)
