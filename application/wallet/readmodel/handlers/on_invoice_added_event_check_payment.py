import datetime
from typing import List

from application.event_publisher import EventHandler
from application.wallet.readmodel.main_dashboard import MainDashboardReadModel, CommitmentDashboardRM, LogItem, MsgType, \
    LogItemType
from infrastructure.db.payments.document_to_wallet_mapping import DocumentToWalletMapping
from infrastructure.db.wallet.main_dashboard_read_model_repository import MainDashboardReadModelRepository
from model.commitments.events import CommitmentAddedEvent
from model.commitments.services.commitments_in_period_service import CommitmentsInPeriodService
from model.commitments.services.params.commitments_calculation_data import CyclicCommitmentDefinition, OccurrenceRange
from model.commons.time import current_date
from model.payments.accounting_document_events import InvoiceAddedEvent
from model.payments.vo.accounting_document_id import AccountingDocumentId


class OnInvoiceAddedEventCheckPaymentHandler(EventHandler):
    __dashboard_read_model_repo: MainDashboardReadModelRepository
    __document_to_wallet_mapping_repo : DocumentToWalletMapping
    def __init__(self,
                 read_model_repository: MainDashboardReadModelRepository,
                 document_to_wallet_mapping_repo: DocumentToWalletMapping):
        super().__init__()
        self.__dashboard_read_model_repo = read_model_repository
        self.__document_to_wallet_mapping_repo = document_to_wallet_mapping_repo

    def handle(self, event: InvoiceAddedEvent):
        super().handle(event)
        if not isinstance(event, InvoiceAddedEvent):
            return
        wallet_id = self.__document_to_wallet_mapping_repo.get(AccountingDocumentId.of(event.aggregate_id))
        dashboard = self.__dashboard_read_model_repo.get_by_wallet_id(str(
            wallet_id
        ))
        if dashboard is None:
            dashboard = MainDashboardReadModel(str(wallet_id))
        if not event.invoice_data.paid_off:
            dashboard.needs_action_log += [LogItem(
                correlated_id=str(event.aggregate_id),
                occurrence_date=event.occurrence_date,
                msg_type=MsgType.INVOICE_WAITS_FOR_PAYMENT,
                type=LogItemType.ACTION_NEED,
                data={}
            )]
        self.__dashboard_read_model_repo.save(dashboard)
