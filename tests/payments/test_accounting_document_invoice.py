from datetime import date
from decimal import Decimal

from model.commons.aggregate_root import AggregateId
from model.commons.vo.correlation_id import CorrelationId
from model.commons.vo.money import Money
from model.commons.vo.unit import Unit
from model.payments.accounting_document import AccountingDocument, Invoice, PaidInvoice
from model.payments.accounting_document_events import DocumentAttachedEvent, InvoiceAddedEvent, \
    AccountingDocumentAddedEvent
from model.payments.commands.add_document_command import AddInvoiceCommand
from model.payments.vo.invoice_data import InvoiceData
from model.payments.vo.invoice_number import InvoiceNumber
from tests.assertion_utils import assert_that_contains_same_event_types_in_order


class TestAccountingDocument:
    WALLET_ID = CorrelationId(AggregateId.generate_new(), "walletagg")
    MONEY_GROSS = Money(Decimal("123"), Unit("USD"))
    RESOURCE_ID = CorrelationId(AggregateId.generate_new(), "resourceagg")
    INVOICE_NUMBER = InvoiceNumber("asdasdasdasd")
    ISSUED_ON = date(2021, 8, 17)

    def test_accounting_document_should_be_invoice_for_add_invoice_command(self):
        # given
        command = self.create_add_invoice_command()
        # when
        result = AccountingDocument.from_add_invoice_command(
            command
        )
        events = result.extract_events_with_state_clearing()

        # then
        assert_that_contains_same_event_types_in_order(events, [
            AccountingDocumentAddedEvent,
            DocumentAttachedEvent,
            InvoiceAddedEvent
        ])

        assert isinstance(
            result, Invoice), f"expected {Invoice.__name__} for aggregate"

        assert not isinstance(
            result, PaidInvoice), f"invoice shouldn't be paid"

    def test_accounting_document_should_be_paid_invoice_for_add_invoice_command_which_is_paid_off(self):
        # given
        command = self.create_add_invoice_command(paid_off=True)
        # when
        result = AccountingDocument.from_add_invoice_command(
            command
        )
        events = result.extract_events_with_state_clearing()

        # then
        assert_that_contains_same_event_types_in_order(events, [
            AccountingDocumentAddedEvent,
            DocumentAttachedEvent,
            InvoiceAddedEvent
        ])

        assert isinstance(
            result, PaidInvoice), f"expected {PaidInvoice.__name__} for aggregate"

    def test_invoice_data_should_add_14_days_to_issued_date_when_deadline_not_provided(self):
        # when
        under_test = InvoiceData.init(self.INVOICE_NUMBER,
                                      self.ISSUED_ON,
                                      paid_off=True)

        # then        
        assert (under_test.deadline - self.ISSUED_ON).days == 14

    def create_add_invoice_command(self, paid_off=False):
        return AddInvoiceCommand(
            wallet=self.WALLET_ID,
            money_gross=self.MONEY_GROSS,
            document_resource_id=self.RESOURCE_ID,
            invoice_data=InvoiceData.init(self.INVOICE_NUMBER,
                                          self.ISSUED_ON,
                                          paid_off=paid_off)
        )
