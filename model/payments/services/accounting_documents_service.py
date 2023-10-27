from typing import Optional, Tuple

from model.commons.result import Fail, Result
from model.payments.accounting_document import AccountingDocument
from model.payments.commands.add_document_command import AddInvoiceCommand
from model.payments.commands.attach_document_command import AttachDocumentCommand
from model.payments.commands.change_invoice_details_command import ChangeInvoiceDetailsCommand
from model.payments.services.payments_service import PaymentService
from model.payments.stores.accounting_documents_store import AccountingDocumentsStore
from model.payments.vo.accounting_document_id import AccountingDocumentId
from model.payments.vo.payment_demand_id import PaymentDemandId
from model.payments.vo.purpose import PaymentCategory


class AccountingDocumentsService:
    def __init__(self,
                 store: AccountingDocumentsStore,
                 payments_service: PaymentService):
        if not isinstance(store, AccountingDocumentsStore):
            raise TypeError(AccountingDocumentsStore)
        self.__store = store
        self.__payments_service = payments_service

    def add_invoice(self, command: AddInvoiceCommand) -> Tuple[AccountingDocumentId, Result]:
        invoice = AccountingDocument.from_add_invoice_command(command)
        return AccountingDocumentId.of(invoice.id), self.__store.save(
            invoice
        )

    def attach_document(self, command: AttachDocumentCommand) -> Result:
        document = self.__store.get_by(command.document_id)
        if not document:
            return Fail("document with given id not found")

        return self.__store.save(
            document.attach_document(command)
        )

    def pay_for_invoice(self, document_id: AccountingDocumentId, category: PaymentCategory) -> Tuple[
        Optional[PaymentDemandId], Result]:
        payment_data, result = self.__store.get_invoice_by(
            document_id).prepare_payment_data(category)

        if not result.succeded() or payment_data is None:
            return None, result if result else Fail("no payment data provided for invoice!")

        return self.__payments_service.pay_for(payment_data)

    def change_invoice_details(self, command: ChangeInvoiceDetailsCommand) -> Result:
        invoice = self.__store.get_invoice_by(command.invoice_id)
        if not invoice:
            return Fail("document with given id not found")

        invoice, result = invoice.change_invoice_details(command)

        return self.__store.save(
            invoice
        ) if result.succeded() else result
