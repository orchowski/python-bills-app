from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Purpose:
    description: str
    category: PaymentCategory


@dataclass(frozen=True)
class PaymentCategory:
    category_id: str
