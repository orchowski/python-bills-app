from application.event_publisher import EventHandler
from application.payments.readmodels.payment_association_rm import PaymentAssociationRM
from infrastructure.db.payments.document_to_wallet_mapping import DocumentToWalletMapping
from infrastructure.db.payments.payment_association_repo import PaymentAssociationRepo
from model.commons.vo.context import WalletId
from model.payments.accounting_document_events import AccountingDocumentAddedEvent
from model.payments.payment_events import PaymentInitiatedEvent
from model.payments.vo.accounting_document_id import AccountingDocumentId


class OnAddAccountingDocumentEventMapWithWalletHandler(EventHandler):
    def __init__(self, mapping_repo: DocumentToWalletMapping):
        self.repo = mapping_repo

    def handle(self, event: AccountingDocumentAddedEvent):
        super().handle(event)
        if not isinstance(event, AccountingDocumentAddedEvent):
            return
        self.repo.correlate(AccountingDocumentId.of(event.aggregate_id), WalletId(event.wallet.id))
