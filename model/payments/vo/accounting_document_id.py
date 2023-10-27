from __future__ import annotations

from uuid import UUID

from model.commons.aggregate_root import AggregateId


class AccountingDocumentId(AggregateId):

    def __init__(self, id: UUID):
        super().__init__(id)
