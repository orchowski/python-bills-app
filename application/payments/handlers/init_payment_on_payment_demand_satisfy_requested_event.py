from application.event_publisher import EventHandler
from model.commons.vo.correlation_id import CorrelationId
from model.payments.commands.payment_requested_command import PaymentRequestedCommand
from model.payments.payment_demand_events import PaymentDemandSatisfyRequestedEvent
from model.payments.services.payments_service import PaymentService


class InitPaymentOnPaymentDemandSatisfyRequestedEvent(EventHandler):
    payments_service: PaymentService

    def __init__(self, payment_service: PaymentService):
        self.payment_service = payment_service

    def handle(self, event: PaymentDemandSatisfyRequestedEvent):
        super().handle(event)
        if not isinstance(event, PaymentDemandSatisfyRequestedEvent):
            return

        self.payment_service.create_payment(
            PaymentRequestedCommand(
                payment_title=event.payment_title,
                money=event.money,
                correlation_id=CorrelationId(event.aggregate_id, "DEMAND"),
                transfer_recipient_data=event.transfer_recipient_data
            )
        )
