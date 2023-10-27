import os
from datetime import timedelta
from decimal import Decimal
from uuid import UUID

from application.payments.dtos.accounting_document_attachment import AccountingDocumentAttachmentDTO
from application.payments.dtos.init_invoice_payment import InitInvoicePaymentDTO
from application.payments.dtos.invoice_add import InvoiceAddDTO
from model.commons.time import current_date
from model.commons.vo.context import Context, WalletId
from model.commons.vo.correlation_id import CorrelationId, CorrelationType
from model.commons.vo.money import Money
from model.commons.vo.unit import Unit
from model.commons.vo.user_id import UserId
from model.payments.accounting_document_events import AccountingDocumentAddedEvent, DocumentAttachedEvent, \
    InvoiceAddedEvent, ChangeInvoiceDetailsEvent
from model.payments.payment_demand_events import PaymentDemandInitiatedEvent, PaymentDemandSatisfyRequestedEvent
from model.payments.payment_events import PaymentInitiatedEvent, PaymentCompletedEvent
from model.payments.vo.invoice_data import InvoiceData, InvoiceIssuer
from model.payments.vo.invoice_number import InvoiceNumber
from model.payments.vo.payment_id import PaymentId
from model.payments.vo.purpose import PaymentCategory
from tests.assertion_utils import assert_that_contains_same_event_types
from tests.common.app_test_config import ApplicationTestingFactory

CONTEXT = Context(UserId("the_user123"), WalletId())
MONEY = Money(Decimal(123), Unit("USD"))
INVOICE_NUMBER = InvoiceNumber("FV123123123")

testing_path = os.path.dirname(__file__)
app = ApplicationTestingFactory()

# TODO configure nimoy test framework or behave to pure BDD
def test_scenario_of_adding_invoice_with_resource():

    accounting_documents_facade = app.accounting_documents_facade()

    document = AccountingDocumentAttachmentDTO(fetch_document(), 'invoice.pdf')

    created_resource, result = accounting_documents_facade.store_accounting_document_attachment_resource(
        document, CONTEXT)

    if result.failed() or not created_resource:
        assert False, f"accounting document save fail: {result.details}"

    invoice_id, add_invoice_result = accounting_documents_facade.add_invoice(InvoiceAddDTO(
        MONEY,
        InvoiceData(
            invoice_number=INVOICE_NUMBER,
            issued_on=current_date(),
            paid_off=False,
            deadline=current_date() + timedelta(days=14)
        ),
        document_resource_id=CorrelationId(
            created_resource.id, CorrelationType.RESOURCE)
    ), CONTEXT)

    if add_invoice_result.failed() or not invoice_id:
        assert False, f"error when add resource to invoice: {add_invoice_result.details}"

    invoice_details_update_result = accounting_documents_facade.change_invoice_details(
        str(invoice_id), InvoiceData(
            invoice_number=INVOICE_NUMBER,
            issued_on=current_date(),
            paid_off=False,
            deadline=current_date() + timedelta(days=14),
            issuer=InvoiceIssuer(app.DEFAULT_RECIPIENT_ID, "Alojzy")
        ),
        CONTEXT
    )

    if invoice_details_update_result.failed():
        assert False, f"error when update invoice {invoice_details_update_result.details}"

    demand_id, invoice_payment_init_result = accounting_documents_facade.init_invoice_payment(
        InitInvoicePaymentDTO(
            str(invoice_id), PaymentCategory("REGULAR_EXPENSES")),
        CONTEXT)

    if invoice_payment_init_result.failed():
        assert False, f"error when init invoice payment: {invoice_payment_init_result.details}"

    app.payments_integration_facade.run_payment(str(demand_id), "przelew 123")

    payment_id = app.payment_association_repo.get_by_associated_id(
        str(demand_id)).payment_id

    payment_completion_result = app.payments_service.complete_payment(
        PaymentId(UUID(payment_id)))

    assert payment_completion_result.succeded(), 'scenario expects succeeded payment, but it\'s not'
    assert_that_contains_same_event_types(app.registered_events.achieved_events, [
        AccountingDocumentAddedEvent, DocumentAttachedEvent, InvoiceAddedEvent, ChangeInvoiceDetailsEvent,
        PaymentDemandInitiatedEvent, PaymentDemandSatisfyRequestedEvent,
        PaymentInitiatedEvent, PaymentCompletedEvent
    ])


def fetch_document():
    with open(f"{testing_path}/example_accounting_document.pdf", "rb") as file:
        return file.read()
