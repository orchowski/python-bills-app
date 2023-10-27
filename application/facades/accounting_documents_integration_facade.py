from typing import Optional, Tuple
from uuid import UUID

from application.payments.dtos.accounting_document_attachment import AccountingDocumentAttachmentDTO
from application.payments.dtos.init_invoice_payment import InitInvoicePaymentDTO
from application.payments.dtos.invoice_add import InvoiceAddDTO
from application.resource.resource import Resource
from application.resource.resource_store import ResourceStore
from model.commons.aggregate_root import AggregateId
from model.commons.result import Result, Success, Fail
from model.commons.time import current_datetime
from model.commons.vo.context import Context
from model.commons.vo.correlation_id import CorrelationId
from model.payments.commands.add_document_command import AddInvoiceCommand
from model.payments.commands.attach_document_command import AttachDocumentCommand
from model.payments.commands.change_invoice_details_command import ChangeInvoiceDetailsCommand
from model.payments.services.accounting_documents_service import AccountingDocumentsService
from model.payments.vo.accounting_document_id import AccountingDocumentId
from model.payments.vo.invoice_data import InvoiceData
from model.payments.vo.payment_demand_id import PaymentDemandId


class AccountingDocumentsIntegrationFacade:
    def __init__(self,
                 resource_store: ResourceStore,
                 accounting_documents_service: AccountingDocumentsService):
        self.__resource_store = resource_store
        self.__accounting_documents_service = accounting_documents_service

    def store_accounting_document_attachment_resource(self, document: AccountingDocumentAttachmentDTO,
                                                      context: Context) -> Tuple[Optional[Resource], Result]:
        new_resource = Resource(
            id=AggregateId.generate_new(),
            date_added=current_datetime(),
            data=document.document_content,
            file_name=document.file_name,
            wallet_id=context.wallet,
            creator=context.user
        )
        resource_store_result = self.__resource_store.save(new_resource)
        # TODO: in the future we can remove new resource when process failed to avoid garbages in DB
        if resource_store_result.failed():
            return None, resource_store_result
        return new_resource, Success()

    def add_invoice(self, invoice_dto: InvoiceAddDTO, context: Context) -> Tuple[Optional[AccountingDocumentId], Result]:
        if invoice_dto.document_resource_id:
            resource = self.__resource_store.get_by(invoice_dto.document_resource_id.id, context)
            if not resource:
                return None, Fail(f'given resource {str(invoice_dto.document_resource_id.id)} does not exist')
        result = self.__accounting_documents_service.add_invoice(
            AddInvoiceCommand(
                wallet=context.wallet,
                money_gross=invoice_dto.money_gross,
                document_resource_id=invoice_dto.document_resource_id,
                invoice_data=invoice_dto.invoice_data
            )
        )
        return result

    # TODO: check context
    def init_invoice_payment(self, init_invoice_payment: InitInvoicePaymentDTO, context: Context) -> Tuple[
        Optional[PaymentDemandId], Result]:
        result = self.__accounting_documents_service.pay_for_invoice(
            AccountingDocumentId(UUID(init_invoice_payment.accounting_document_id)),
            init_invoice_payment.payment_category
        )
        return result

    # TODO: check context
    # TODO: create read model for invoices etc.
    def change_invoice_details(self, invoice_id: str, invoice_data: InvoiceData, context: Context) -> Result:
        try:
            return self.__accounting_documents_service.change_invoice_details(
                ChangeInvoiceDetailsCommand(
                    AccountingDocumentId(UUID(invoice_id)), invoice_data
                )
            )
        except ValueError as e:
            return Fail(str(e))

    # TODO: check context
    def join_resource_to_document(self, resource_id: AggregateId, document_id: AccountingDocumentId,
                                  context: Context) -> Result:

        resource = self.__resource_store.get_by(resource_id, context)
        if not resource:
            return Fail(f'given resource {str(resource_id)} does not exist')
        attaching_result = self.__accounting_documents_service.attach_document(
            AttachDocumentCommand(
                document_id=document_id,
                document_resource_id=CorrelationId(resource_id, "RESOURCE")
            )
        )
        return attaching_result

    def store_receipt(self) -> AccountingDocumentId:
        return None
