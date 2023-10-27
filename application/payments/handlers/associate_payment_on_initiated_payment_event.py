from application.event_publisher import EventHandler
from application.payments.readmodels.payment_association_rm import PaymentAssociationRM
from infrastructure.db.payments.payment_association_repo import PaymentAssociationRepo
from model.payments.payment_events import PaymentInitiatedEvent


class AssociatePaymentOnPaymentInitiatedEvent(EventHandler):
    def __init__(self, payment_association_repo: PaymentAssociationRepo):
        self.payment_association_repo = payment_association_repo

    def handle(self, event: PaymentInitiatedEvent):
        super().handle(event)
        if not isinstance(event, PaymentInitiatedEvent):
            return

        self.payment_association_repo.save(
            PaymentAssociationRM(
                payment_id=str(event.aggregate_id),
                associations={(str(event.correlation_id.id),
                               event.correlation_id.correlation_type)}
            ))
