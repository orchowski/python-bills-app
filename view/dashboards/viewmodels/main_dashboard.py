from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import List

from pydantic import BaseModel

from application.wallet.readmodel.main_dashboard import MainDashboardReadModel


class CommitmentView(BaseModel):
    id: str
    title: str
    money: Decimal
    unit: str
    deadline: date


class LogItemView(BaseModel):
    correlated_id: str
    title: str
    occurrence_date: datetime


class MainDashboardView(BaseModel):
    commitments_upcoming: List[CommitmentView]
    payments_log: List[LogItemView]
    needs_action_log: List[LogItemView]

    @classmethod
    def from_read_model(cls, rm: MainDashboardReadModel) -> MainDashboardView:
        if rm is None:
            return cls(commitments_upcoming=[], payments_log=[], needs_action_log=[])
        return cls(
            commitments_upcoming=[CommitmentView(
                id=i.id,
                title=i.title,
                money=i.money,
                unit=i.unit,
                deadline=i.deadline
            ) for i in rm.commitments_upcoming],
            payments_log=[LogItemView(
                correlated_id=i.correlated_id,
                # TODO : place to handle translations
                title=f"{i.msg_type.name} : that will be translated with adding {i.data}",
                occurrence_date=i.occurrence_date
            ) for i in rm.payments_log],
            needs_action_log=[LogItemView(
                correlated_id=i.correlated_id,
                # TODO : place to handle translations
                title=f"{i.msg_type.name} : that will be translated with adding {i.data}",
                occurrence_date=i.occurrence_date
            ) for i in rm.needs_action_log]
        )
