from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from model.commons.aggregate_root import AggregateId
from model.commons.vo.user_id import UserId
from model.commons.vo.correlation_id import CorrelationType

@dataclass
class Context:
    user: UserId
    wallet: WalletId


# TODO: it's temporary and just like correlation_id. We can leave it and inherit correlation later
class WalletId:
    def __init__(self, id: AggregateId = None) -> None:
        if id:
            self.id = id
        else:
            self.id = AggregateId(UUID("123e4567-e89b-12d3-a456-426614174000"))
        self.correlated_aggregate_type = CorrelationType.WALLET

    def __str__(self):
        return repr(self.id)

    def __eq__(self, o: object) -> bool:
        return type(o) == WalletId and o.id == self.id

    def __hash__(self) -> int:
        return hash(self)
