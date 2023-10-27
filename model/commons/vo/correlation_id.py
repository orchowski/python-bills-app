from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from model.commons.aggregate_root import AggregateId


@dataclass(frozen=True)
class CorrelationId:
    id: AggregateId
    correlation_type: CorrelationType


class CorrelationType(Enum):
    REMINDER_NOTE = "REMINDER_NOTE"
    PAYMENT = "PAYMENT"
    WALLET = "WALLET"
    RESOURCE = "RESOURCE"
    ACCOUNTING_DOCUMENT = "ACCOUNTING_DOCUMENT"
    INVOICE = "INVOICE"
    COMMITMENT = "COMMITMENT"
