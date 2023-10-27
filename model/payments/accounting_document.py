from __future__ import annotations

from datetime import date
from typing import TypeVar, Type, Tuple, Optional

from model.commons.aggregate_root import AggregateRoot
from model.commons.result import Fail, Result, Success
from model.commons.time import current_date
from model.commons.vo.correlation_id import CorrelationId
from model.commons.vo.money import Money
from model.commons.vo.user_id import UserId
from model.payments.accounting_document_events import AccountingDocumentAddedEvent, ChangeInvoiceDetailsEvent, \
    DocumentAttachedEvent, InvoiceAddedEvent
from model.payments.commands.add_document_command import AddInvoiceCommand
from model.payments.commands.attach_document_command import AttachDocumentCommand
from model.payments.commands.change_invoice_details_command import ChangeInvoiceDetailsCommand
from model.payments.payment_events import PaymentCompletedEvent
from model.payments.vo.accounting_document_id import AccountingDocumentId
from model.payments.vo.invoice_data import InvoiceData, InvoiceIssuer
from model.payments.vo.invoice_number import InvoiceNumber
from model.payments.vo.payment_data import PaymentData
from model.payments.vo.purpose import PaymentCategory, Purpose

AD = TypeVar('AD', bound='AccountingDocument')


class AccountingDocument(AggregateRoot):
    wallet: CorrelationId
    money_gross: Money
    document_resource_id: Optional[CorrelationId]

    def __init__(
            self,
            id: AccountingDocumentId,
            aggregate_version: int,
            wallet: CorrelationId,
            money_gross: Money,
            document_resource_id: Optional[CorrelationId]
    ):
        super().__init__(id, aggregate_version)
        self.money_gross = money_gross
        self.wallet = wallet
        self.document_resource_id = document_resource_id

    def settle(self) -> Tuple[AccountingDocument, Result]:
        return (
            self.apply(
                PaymentCompletedEvent.create(self)
            ),
            Success()
        )

    def attach_document(self, command: AttachDocumentCommand) -> AccountingDocument:
        return self.apply(
            DocumentAttachedEvent.create(self, command.document_resource_id)
        )

    def prepare_payment_data(self, category: PaymentCategory) -> Tuple[Optional[PaymentData], Result]:
        return (None, Fail("Provide more data for accounting document"))

    @classmethod
    def from_add_invoice_command(cls, command: AddInvoiceCommand) -> AccountingDocument:
        document = AccountingDocument.shell().apply(
            AccountingDocumentAddedEvent.create(
                aggregate_id=AccountingDocumentId.generate_new(),
                money_gross=command.money_gross,
                wallet=command.wallet,
                document_resource_id=None
            )
        )
        if command.document_resource_id:
            document = document.apply(
                DocumentAttachedEvent.create(aggregate=document, document_resource_id=command.document_resource_id)
            )
        return document.apply(
            InvoiceAddedEvent.create(
                document,
                command.invoice_data
            )
        )

    def apply_document_added(self, event: AccountingDocumentAddedEvent) -> AccountingDocument:
        return AccountingDocument(
            id=AccountingDocumentId.of(event.aggregate_id),
            aggregate_version=event.aggregate_version,
            wallet=event.wallet,
            money_gross=event.money_gross,
            document_resource_id=event.document_resource_id
        )

    def apply_invoice_added(self, event: InvoiceAddedEvent) -> Invoice:
        init = PaidInvoice if event.invoice_data.paid_off else Invoice
        return init(
            AccountingDocumentId.of(self.id),
            event.aggregate_version,
            self.wallet,
            self.money_gross,
            self.document_resource_id,
            event.invoice_data
        )

    def apply_document_attached(self, event: DocumentAttachedEvent) -> AccountingDocument:
        document_to_apply = self.copy(self)
        document_to_apply.document_resource_id = event.document_resource_id
        document_to_apply.aggregate_version = event.aggregate_version
        return document_to_apply

    @classmethod
    def shell(cls: Type[AD]) -> AD:
        return cls(None, None, None, None, None)

    @classmethod
    def copy(cls: Type[AD], another_document: AccountingDocument) -> AD:
        return cls(
            AccountingDocumentId.of(another_document.id),
            another_document.aggregate_version,
            wallet=another_document.wallet,
            money_gross=another_document.money_gross,
            document_resource_id=another_document.document_resource_id
        )


INV = TypeVar('INV', bound='Invoice')


class Invoice(AccountingDocument):
    invoice_number: InvoiceNumber
    issued_on: date
    deadline: date
    issuer: Optional[InvoiceIssuer] = None
    originator: Optional[UserId] = None
    tax_money: Optional[Money] = None

    def __init__(self, id: AccountingDocumentId,
                 aggregate_version: int,
                 wallet: CorrelationId,
                 money_gross: Money,
                 document_resource_id: Optional[CorrelationId],
                 invoice_data: InvoiceData):
        super().__init__(id, aggregate_version, wallet, money_gross, document_resource_id)

        self.invoice_number = invoice_data.invoice_number
        self.issued_on = invoice_data.issued_on
        self.issuer = invoice_data.issuer
        self.originator = invoice_data.originator
        self.deadline = invoice_data.deadline
        self.tax_money = invoice_data.tax_money

    def is_paid(self) -> bool:
        return False

    def prepare_payment_data(self, category: PaymentCategory) -> Tuple[Optional[PaymentData], Result]:
        if self.issuer is None:
            return None, Fail("issuer not provided, fill invoice data")

        return (PaymentData(
            money=self.money_gross,
            payment_deadline=self.deadline,
            purpose=Purpose(str(self.invoice_number), category),
            correlation_id=CorrelationId(self.id, type(self).__name__),
            recipient_id=self.issuer.id
        ), Success())

    def change_invoice_details(self, command: ChangeInvoiceDetailsCommand) -> Tuple[Invoice, Result]:
        return self.apply(ChangeInvoiceDetailsEvent.create(
            self,
            command.invoice_data
        )), Success()

    def apply_change_invoice_details(self, event: ChangeInvoiceDetailsEvent) -> Invoice:
        invoice_to_apply = self.copy(self)
        invoice_to_apply.invoice_number = event.invoice_data.invoice_number
        invoice_to_apply.issued_on = event.invoice_data.issued_on
        invoice_to_apply.deadline = event.invoice_data.deadline
        invoice_to_apply.issuer = event.invoice_data.issuer
        invoice_to_apply.originator = event.invoice_data.originator
        invoice_to_apply.tax_money = event.invoice_data.tax_money
        invoice_to_apply.aggregate_version = event.aggregate_version
        return invoice_to_apply

    @classmethod
    def copy(cls: Type[INV], another_invoice: Invoice) -> INV:
        return cls(
            AccountingDocumentId.of(another_invoice.id),
            another_invoice.aggregate_version,
            wallet=another_invoice.wallet,
            money_gross=another_invoice.money_gross,
            document_resource_id=another_invoice.document_resource_id,
            invoice_data=InvoiceData(
                another_invoice.invoice_number,
                current_date(),
                another_invoice.is_paid(),
                another_invoice.deadline,
                issuer=another_invoice.issuer,
                originator=another_invoice.originator,
                tax_money=another_invoice.tax_money
            )
        )

    @classmethod
    def shell(cls: Type[AD]) -> AD:
        return cls(None, None, None, None, None)


class PaidInvoice(Invoice):
    def is_paid(self) -> bool:
        return True


class Receipt(AccountingDocument):
    pass
