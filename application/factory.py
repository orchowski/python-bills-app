from flask_peewee.db import PostgresqlDatabase

from application.authentication.auth_db import initialize_database as auth_db_init
from application.commitments.on_add_commitment_handler import OnAddCommitmentEventUpdateCommitmentReadModel
from application.commitments.on_commitment_activated import OnCommitmentActivatedUpdateCommitmentReadModelHandler
from application.commitments.on_commitment_amount_changed import \
    OnCommitmentAmountChangedUpdateCommitmentReadModelHandler
from application.commitments.on_commitment_deactivated import OnCommitmentDeactivatedUpdateCommitmentReadModelHandler
from application.commitments.on_commitment_metadata_updated import \
    OnCommitmentMetadataUpdatedUpdateCommitmentReadModelHandler
from application.commitments.on_commitment_repeat_period_changed import \
    OnCommitmentRepeatPeriodChangedUpdateCommitmentReadModelHandler
from application.commitments.services.commitments_read_service import CommitmentsReadService
from application.event_publisher import DefaultEventPublisher
from application.facades.accounting_documents_integration_facade import AccountingDocumentsIntegrationFacade
from application.facades.commitment_integration_facade import CommitmentIntegrationFacade
from application.payments.handlers.on_add_accounting_document_event_map_with_wallet import \
    OnAddAccountingDocumentEventMapWithWalletHandler
from application.wallet.readmodel.handlers.on_commitment_added_update_main_dashboard import \
    OnCommitmentAddedEventUpdateMainDashboard
from application.wallet.readmodel.handlers.on_invoice_added_event_check_payment import \
    OnInvoiceAddedEventCheckPaymentHandler
from infrastructure.db.commitment_read_model_repository import CommitmentReadModelRepository
from infrastructure.db.commitment_repository import CommitmentRepository
from infrastructure.db.payments.accounting_documents_repo import AccountingDocumentsRepository
from infrastructure.db.payments.bank_transfer_recipients_rm_repo import BankTransferRecipientsRMRepository
from infrastructure.db.payments.document_to_wallet_mapping import DocumentToWalletMapping
from infrastructure.db.payments.payment_demand_repository import PaymentDemandRepository
from infrastructure.db.payments.payment_repository import PaymentRepository
from infrastructure.db.resource_repository import ResourceRepository
from infrastructure.db.wallet.main_dashboard_read_model_repository import MainDashboardReadModelRepository
from model.commitments.services.commitment_service import CommitmentService
from model.commitments.services.commitments_in_period_service import CommitmentsInPeriodService
from model.commitments.stores.commitment_store import CommitmentStore
from model.commons.aggregate_store import EventPublisher
from model.payments.services.accounting_documents_service import AccountingDocumentsService
from model.payments.services.payments_service import PaymentService


class ApplicationFactory:
    __commitments_repo: CommitmentRepository
    __commitments_read_model_repo: CommitmentReadModelRepository
    __commitments_integration_facade: CommitmentIntegrationFacade
    __commitments_in_period_service: CommitmentsInPeriodService
    __main_dashboard_read_model_repo: MainDashboardReadModelRepository
    __document_to_wallet_mapping_repo: DocumentToWalletMapping
    __accounting_documents_integration_facade: AccountingDocumentsIntegrationFacade

    def __init__(self):
        self.__document_to_wallet_mapping_repo = DocumentToWalletMapping()
        self.__commitments_read_model_repo = CommitmentReadModelRepository()
        self.__main_dashboard_read_model_repo = MainDashboardReadModelRepository()
        self.__commitments_in_period_service = CommitmentsInPeriodService(self.__commitments_read_model_repo)
        self.__event_publisher = DefaultEventPublisher([
            OnAddCommitmentEventUpdateCommitmentReadModel(self.__commitments_read_model_repo),
            OnCommitmentAmountChangedUpdateCommitmentReadModelHandler(self.__commitments_read_model_repo),
            OnCommitmentActivatedUpdateCommitmentReadModelHandler(self.__commitments_read_model_repo),
            OnCommitmentDeactivatedUpdateCommitmentReadModelHandler(self.__commitments_read_model_repo),
            OnCommitmentMetadataUpdatedUpdateCommitmentReadModelHandler(self.__commitments_read_model_repo),
            OnCommitmentRepeatPeriodChangedUpdateCommitmentReadModelHandler(self.__commitments_read_model_repo),
            OnCommitmentAddedEventUpdateMainDashboard(self.__main_dashboard_read_model_repo, self.__commitments_in_period_service),
            OnAddAccountingDocumentEventMapWithWalletHandler(self.__document_to_wallet_mapping_repo),
            OnInvoiceAddedEventCheckPaymentHandler(self.__main_dashboard_read_model_repo, self.__document_to_wallet_mapping_repo)
        ])
        self.__commitments_repo = CommitmentRepository(self.__event_publisher)
        self.__commitments_read_service = CommitmentsReadService(self.__commitments_read_model_repo)
        self.__commitments_integration_facade = CommitmentIntegrationFacade(CommitmentService(self.__commitments_repo),
                                                                            self.__commitments_repo,
                                                                            self.__commitments_read_service
                                                                            )
        #         ------------- ACCOUNTING DOCUMENTS ------------
        self.__resource_store = ResourceRepository()
        self.__accounting_document_repo = AccountingDocumentsRepository(
            self.__event_publisher)
        self.__payment_demand_repo = PaymentDemandRepository(self.__event_publisher)
        self.__payment_store = PaymentRepository(self.__event_publisher)

        self.__payments_service = PaymentService(
            BankTransferRecipientsRMRepository([]),
            self.__payment_demand_repo,
            self.__payment_store)

        self.__accounting_documents_service = AccountingDocumentsService(
            store=self.__accounting_document_repo,
            payments_service=self.__payments_service
        )
        self.__accounting_documents_integration_facade = AccountingDocumentsIntegrationFacade(
            self.__resource_store,
            self.__accounting_documents_service
        )
        auth_db_init(
            PostgresqlDatabase('postgres', user='postgres', password='aleksander', host='127.0.0.1', port=5432))

    def accounting_documents_integration_facade(self) -> AccountingDocumentsIntegrationFacade:
        return self.__accounting_documents_integration_facade

    def commitment_integration_facade(self) -> CommitmentIntegrationFacade:
        return self.__commitments_integration_facade

    def commitments_store(self) -> CommitmentStore:
        return self.__commitments_repo

    def commitments_read_model_repository(self) -> CommitmentReadModelRepository:
        return self.__commitments_read_model_repo

    def main_dashboard_read_model_repo(self) -> MainDashboardReadModelRepository:
        return self.__main_dashboard_read_model_repo

    def event_publisher(self) -> EventPublisher:
        return self.__event_publisher
