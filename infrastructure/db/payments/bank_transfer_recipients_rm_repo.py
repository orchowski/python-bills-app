from typing import List, Optional

from model.payments.stores.bank_transfer_recipients_rm_store import BankTransferRecipientsRMStore
from model.payments.vo.transfer_recipient_data import TransferRecipientData


class BankTransferRecipientsRMRepository(BankTransferRecipientsRMStore):
    recipients: List[TransferRecipientData]

    def __init__(self, recipients: List[TransferRecipientData] = None):
        self.recipients = recipients if recipients else []

    def save(self, recipient_data: TransferRecipientData):
        self.recipients.append(recipient_data)

    def get_by_id(self, recipient_id: str) -> Optional[TransferRecipientData]:
        return next((recipient for recipient in self.recipients if recipient.id == recipient_id), None)
