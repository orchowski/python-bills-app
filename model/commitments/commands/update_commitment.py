from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from model.commitments.vo.commitment_id import CommitmentId
from model.commitments.vo.metadata import Metadata
from model.commitments.vo.period import Period
from model.commons.vo.context import Context


@dataclass()
class UpdateCommitment:
    id: CommitmentId
    amount: Decimal
    unit: str
    context: Context
    metadata: Metadata
    start_date: date
    repeat_period: Period
    every_period: int
    active: bool
