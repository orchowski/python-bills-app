from dataclasses import dataclass
from decimal import Decimal

from model.commons.vo.unit import Unit


@dataclass(frozen=True)
class Money:
    amount: Decimal
    unit: Unit
