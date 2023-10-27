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
from application.facades.payments_integration_facade import PaymentsIntegrationFacade
from application.payments.handlers.associate_payment_on_initiated_payment_event import \
    AssociatePaymentOnPaymentInitiatedEvent
from application.payments.handlers.init_payment_on_payment_demand_satisfy_requested_event import \
    InitPaymentOnPaymentDemandSatisfyRequestedEvent
from application.resource.resource_store import ResourceStore
from application.wallet.readmodel.handlers.on_commitment_added_update_main_dashboard import \
    OnCommitmentAddedEventUpdateMainDashboard
from infrastructure.db.commitment_repository import CommitmentRepository
from infrastructure.db.payments.accounting_documents_repo import AccountingDocumentsRepository
from infrastructure.db.payments.bank_transfer_recipients_rm_repo import BankTransferRecipientsRMRepository
from infrastructure.db.payments.payment_association_repo import PaymentAssociationRepo
from infrastructure.db.payments.payment_demand_repository import PaymentDemandRepository
from infrastructure.db.payments.payment_repository import PaymentRepository
from infrastructure.db.resource_repository import ResourceRepository
from infrastructure.db.wallet.main_dashboard_read_model_repository import MainDashboardReadModelRepository
from model.commitments.services.commitment_service import CommitmentService
from model.commitments.stores.commitment_store import CommitmentStore
from model.commons.aggregate_store import EventPublisher
from model.payments.services.accounting_documents_service import AccountingDocumentsService
from model.payments.services.payments_service import PaymentService
from model.payments.vo.transfer_recipient_data import TransferRecipientData
from model.commitments.services.commitments_in_period_service import CommitmentsInPeriodService
from tests.commitments.mocks.commitment_read_model_repository import TestCommitmentReadModelRepository
from tests.common.mocks.registering_event_handler import RegisteringEventHandler


class ApplicationTestingFactory:
    DEFAULT_RECIPIENT_ID = '274-a-sdas-r32r-d-168'
    commitments_repo: CommitmentRepository
    commitments_read_model_repo: TestCommitmentReadModelRepository
    commitment_integration_facade: CommitmentIntegrationFacade
    payments_integration_facade: PaymentsIntegrationFacade
    accounting_documents_integration_facade: AccountingDocumentsIntegrationFacade
    accounting_documents_service: AccountingDocumentsService
    resource_store: ResourceStore
    payments_service: PaymentService
    event_publisher: EventPublisher
    payment_association_repo: PaymentAssociationRepo
    commitments_in_period_service: CommitmentsInPeriodService
    registered_events: RegisteringEventHandler

    def __init__(self):
        self.registered_events = RegisteringEventHandler()
        self.commitments_read_model_repo = TestCommitmentReadModelRepository()
        self.payment_association_repo = PaymentAssociationRepo()
        self.event_publisher = DefaultEventPublisher([])
        self.payment_store = PaymentRepository(self.event_publisher)
        accounting_document_repo = AccountingDocumentsRepository(
            self.event_publisher)
        payment_demand_repo = PaymentDemandRepository(self.event_publisher)
        self.payments_service = PaymentService(
            BankTransferRecipientsRMRepository([TransferRecipientData(self.DEFAULT_RECIPIENT_ID,
                                                                      "Alojzy Wiśniówka sp. z o.o.o",
                                                                      "PL61109010140000071219812874")]),
            payment_demand_repo,
            self.payment_store)
        self.resource_store = ResourceRepository()
        self.accounting_documents_service = AccountingDocumentsService(
            store=accounting_document_repo,
            payments_service=self.payments_service
        )
        self.commitments_repo = CommitmentRepository(self.event_publisher)
        self.commitments_service = CommitmentService(self.commitments_repo)
        self.commitment_integration_facade = CommitmentIntegrationFacade(
            self.commitments_service, self.commitments_repo, CommitmentsReadService(self.commitments_read_model_repo))
        self.payments_integration_facade = PaymentsIntegrationFacade(
            self.payments_service)
        self.accounting_documents_integration_facade = AccountingDocumentsIntegrationFacade(
            self.resource_store,
            self.accounting_documents_service
        )

        self.main_dashboard_read_model_repo = MainDashboardReadModelRepository()
        self.commitments_in_period_service = CommitmentsInPeriodService(self.commitments_read_model_repo)

        self.event_publisher.register(
            [
                OnAddCommitmentEventUpdateCommitmentReadModel(self.commitments_read_model_repo),
                OnCommitmentAmountChangedUpdateCommitmentReadModelHandler(self.commitments_read_model_repo),
                OnCommitmentActivatedUpdateCommitmentReadModelHandler(self.commitments_read_model_repo),
                OnCommitmentDeactivatedUpdateCommitmentReadModelHandler(self.commitments_read_model_repo),
                OnCommitmentMetadataUpdatedUpdateCommitmentReadModelHandler(self.commitments_read_model_repo),
                OnCommitmentRepeatPeriodChangedUpdateCommitmentReadModelHandler(self.commitments_read_model_repo),
                InitPaymentOnPaymentDemandSatisfyRequestedEvent(self.payments_service),
                AssociatePaymentOnPaymentInitiatedEvent(self.payment_association_repo),
                OnCommitmentAddedEventUpdateMainDashboard(self.main_dashboard_read_model_repo, self.commitments_in_period_service),
                self.registered_events
            ]
        )

    def commitment_integration_facade(self) -> CommitmentIntegrationFacade:
        return self.commitment_integration_facade

    def accounting_documents_facade(self) -> AccountingDocumentsIntegrationFacade:
        return self.accounting_documents_integration_facade

    def commitment_store(self) -> CommitmentStore:
        return self.commitments_repo

    def commitments_read_model_repository(self) -> TestCommitmentReadModelRepository:
        return self.commitments_read_model_repo
