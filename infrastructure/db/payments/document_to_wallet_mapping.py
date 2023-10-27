from typing import Dict
from typing import Optional

from model.commons.vo.context import WalletId
from model.payments.vo.accounting_document_id import AccountingDocumentId


class DocumentToWalletMapping:
    __mappings: Dict[AccountingDocumentId, WalletId] = {}

    def correlate(self, document_id: AccountingDocumentId, wallet_id: WalletId):
        self.__mappings[document_id] = wallet_id

    def get(self, document_id: AccountingDocumentId) -> Optional[WalletId]:
        return self.__mappings.get(document_id)
