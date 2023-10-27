import os

from flask import Blueprint, request, flash, jsonify, make_response
from pydantic import ValidationError
from werkzeug.utils import secure_filename

from application.factory import ApplicationFactory
from application.payments.dtos.accounting_document_attachment import AccountingDocumentAttachmentDTO
from application.payments.dtos.invoice_add import InvoiceAddDTO
from model.commons.aggregate_root import AggregateId
from model.commons.vo.context import Context, WalletId
from model.commons.vo.correlation_id import CorrelationId, CorrelationType
from model.commons.vo.money import Money
from model.commons.vo.unit import Unit
from model.commons.vo.user_id import UserId
from model.payments.vo.invoice_data import InvoiceData, InvoiceIssuer
from model.payments.vo.invoice_number import InvoiceNumber
from view.helpers.request_helpers import create_response, parse_request_body
from view.payments.models.invoices.add_invoice_request import AddInvoiceRequest
from view.payments.models.invoices.change_invoice_request import ChangeInvoiceRequest

accounting_documents_router = Blueprint('accounting_documents', __name__)


def app() -> ApplicationFactory:
    return accounting_documents_router.app


def context() -> Context:
    return Context(UserId("testuser"), WalletId())


@accounting_documents_router.route('/accounting_documents/resources', methods=['POST'])
def upload_resource_accounting_document():
    if 'file' not in request.files:
        return jsonify({"message": "form-data 'file' parameter is required"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "no file"})

    file_name = secure_filename(file.filename)
    file_bytes = file.stream.read()

    created_resource, result = app().accounting_documents_integration_facade().store_accounting_document_attachment_resource(
        AccountingDocumentAttachmentDTO(
            file_bytes, file_name
        ), context())
    return create_response({"resourceId": str(created_resource.id)}, 201) if result.succeded() else create_response(
        {"message": result.details}, 400
    )


@accounting_documents_router.route('/accounting_documents/invoices', methods=['POST'])
def add_invoice():
    try:
        add_invoice_request = parse_request_body(AddInvoiceRequest, request)
    except ValidationError as e:
        return make_response(e.json(), 400)
    invoice_id, result = app().accounting_documents_integration_facade().add_invoice(
        InvoiceAddDTO(
            money_gross=Money(
                amount=add_invoice_request.money_gross,
                unit=Unit(add_invoice_request.unit),
            ),
            invoice_data=InvoiceData.init(
                invoice_number=InvoiceNumber(add_invoice_request.invoice_number),
                issued_on=add_invoice_request.issued_on,
                paid_off=add_invoice_request.paid_off,
                deadline=add_invoice_request.deadline,
                issuer=None if not add_invoice_request.issuer else InvoiceIssuer(add_invoice_request.issuer.id,
                                                                                 add_invoice_request.issuer.name),
                originator=None if not add_invoice_request.originator else UserId(add_invoice_request.originator),
                tax_money=None if not add_invoice_request.tax_money else Money(add_invoice_request.tax_money,
                                                                               add_invoice_request.unit),
            ),
            document_resource_id=None if not add_invoice_request.document_resource else CorrelationId(
                AggregateId(add_invoice_request.document_resource), CorrelationType.RESOURCE)
        ),
        context()
    )

    return create_response({"invoiceId": str(invoice_id)}, 201) if result.succeded() else create_response(
        {"message": result.details}, 400)

@accounting_documents_router.route('/accounting_documents/invoices/<invoice_id>', methods=['PUT'])
def change_invoice(invoice_id):
    try:
        change_invoice_request = parse_request_body(ChangeInvoiceRequest, request)
    except ValidationError as e:
        return make_response(e.json(), 400)
    result = app().accounting_documents_integration_facade().change_invoice_details(
        invoice_id,
        InvoiceData.init(
            invoice_number=InvoiceNumber(change_invoice_request.invoice_number),
            issued_on=change_invoice_request.issued_on,
            paid_off=change_invoice_request.paid_off,
            deadline=change_invoice_request.deadline,
            issuer=None if not change_invoice_request.issuer else InvoiceIssuer(change_invoice_request.issuer.id,
                                                                             change_invoice_request.issuer.name),
            originator=None if not change_invoice_request.originator else UserId(change_invoice_request.originator),
            tax_money=None if not change_invoice_request.tax_money else Money(change_invoice_request.tax_money,
                                                                           change_invoice_request.unit),
        ),
        context()
    )
    return make_response('', 204) if result.succeded() else create_response(
        {"message": result.details}, 400)