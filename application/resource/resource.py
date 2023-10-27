from dataclasses import dataclass
from datetime import datetime

from model.commons.aggregate_root import AggregateId
from model.commons.vo.context import WalletId
from model.commons.vo.user_id import UserId


@dataclass()
class Resource:
    id: AggregateId
    date_added: datetime
    data: bytes
    file_name: str
    wallet_id: WalletId
    creator: UserId
