from abc import abstractmethod
from typing import Optional

from model.payments.vo.transfer_recipient_data import TransferRecipientData


class BankTransferRecipientsRMStore:
    @abstractmethod
    def save(self, recipient_data: TransferRecipientData):
        raise NotImplementedError()

    @abstractmethod
    def get_by_id(self, recipient_id: str) -> Optional[TransferRecipientData]:
        raise NotImplementedError()
