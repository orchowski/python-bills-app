import decimal
import uuid
from datetime import timedelta

from flask import Blueprint
from flask import jsonify

from application.factory import ApplicationFactory
from application.payments.dtos.invoice_add import InvoiceAddDTO
from model.commitments.vo.period import Period
from model.commons.aggregate_root import EventId
from model.commons.time import current_date, current_datetime
from model.commons.vo.context import Context, WalletId
from model.commons.vo.correlation_id import CorrelationId
from model.commons.vo.money import Money
from model.commons.vo.unit import Unit
from model.commons.vo.user_id import UserId
from model.payments.accounting_document import Invoice
from model.payments.accounting_document_events import InvoiceAddedEvent, AccountingDocumentAddedEvent
from model.payments.vo.accounting_document_id import AccountingDocumentId
from model.payments.vo.invoice_data import InvoiceData, InvoiceIssuer
from model.payments.vo.invoice_number import InvoiceNumber
from tests.commitments.services.test_commitments_service import create_add_commitment_command
from view.dashboards.viewmodels.main_dashboard import MainDashboardView
from view.helpers.request_helpers import create_response

dashboard_router = Blueprint('dashboard', __name__)


@dashboard_router.route('/dashboards/main', methods=['GET'])
def get_dashboard():
    a_context = Context(UserId('jakska'), WalletId())
    dashboard = dashboard_router.app.main_dashboard_read_model_repo().get_by_wallet_id(str(a_context.wallet.id))
    return create_response(MainDashboardView.from_read_model(dashboard).dict())


@dashboard_router.route('/test/dashboards/main/add_commitment', methods=['GET'])
def add_testing_commitment():
    res = dashboard_router.app.commitment_integration_facade().add_new_commitment(
        create_add_commitment_command(repeat_period=Period.WEEK, every_period=1)
    )

    aggregate_id = AccountingDocumentId.generate_new()
    dashboard_router.app.event_publisher().publish(
        AccountingDocumentAddedEvent(
            None,
            aggregate_id,
            2,
            None,
            None,
            WalletId(),
            None
        )
    )
    dashboard_router.app.event_publisher().publish(
        InvoiceAddedEvent(
            event_id=EventId.new(),
            aggregate_id=aggregate_id,
            aggregate_version=2,
            occurrence_date=current_datetime(),
            invoice_data=InvoiceData(
                invoice_number=InvoiceNumber("asdasd"),
                issued_on=current_date(),
                paid_off=False,
                deadline=current_date() + timedelta(days=14),
                issuer=InvoiceIssuer("123", "Alojzy")
            )
        )
    )
    return jsonify({
        'createdCommitment': str(res),
    }
    )
