from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from model.commitments.commitment import CommitmentAddedEvent
from model.commitments.vo.period import Period


@dataclass()
class CommitmentReadModel:
    id: str
    amount: Decimal
    unit: str
    title: str
    description: str
    creation_date: datetime
    modification_date: datetime
    start_date: date
    repeat_period: Period
    wallet_id: str
    active: bool = True
    every_period: int = 1

    @classmethod
    def of(cls, event: CommitmentAddedEvent):
        return cls(
            id=str(event.aggregate_id),
            amount=event.amount,
            unit=event.unit.name,
            title=event.metadata.title,
            description=event.metadata.description,
            creation_date=event.occurrence_date,
            modification_date=event.occurrence_date,
            active=event.active,
            start_date=event.repeat_period.start_date,
            repeat_period=event.repeat_period.period,
            every_period=event.repeat_period.every,
            wallet_id=str(event.wallet_id.id)
        )