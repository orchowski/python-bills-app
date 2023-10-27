from __future__ import annotations

import decimal
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import List


# TODO : work on naming
@dataclass
class MainDashboardReadModel:
    wallet_id: str
    commitments_upcoming: List[CommitmentDashboardRM] = field(default_factory=lambda: [])
    # It also can be single list to split on view lever, but it may be problematic because we'd have to fetch all items potentially
    payments_log: List[LogItem] = field(default_factory=lambda: [])
    needs_action_log: List[LogItem] = field(default_factory=lambda: [])


@dataclass
class CommitmentDashboardRM:
    id: str
    title: str
    money: decimal.Decimal
    unit: str
    deadline: date


class MsgType(Enum):
#     COMMITMENTS
    PAYMENT_FINISHED = "PAYMENT_FINISHED"
#     NEEDS ACTION
    INVOICE_WAITS_FOR_PAYMENT = "INVOICE_WAITS_FOR_PAYMENT"


@dataclass
class LogItem:
    correlated_id: str
    occurrence_date: datetime
    msg_type: MsgType
    type: LogItemType
    data: dict


class LogItemType(Enum):
    ACTION_NEED = "ACTION_NEED"
    PAYMENT = "PAYMENT"
