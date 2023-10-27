from typing import List

from application.payments.readmodels.payment_association_rm import Id, PaymentAssociationRM, PaymentID


class PaymentAssociationRepo:
    payment_assotiations: List[PaymentAssociationRM] = []

    def save(self, association: PaymentAssociationRM):
        self.payment_assotiations.append(association)

    def update(self, association: PaymentAssociationRM):
        self.delete(
            association.payment_id
        )
        self.save(association)

    def delete(self, payment_id: PaymentID):
        self.payment_assotiations.remove(self.get_by_id(payment_id))

    def get_all(self) -> List[PaymentAssociationRM]:
        return self.payment_assotiations

    def get_by_id(self, payment_id: PaymentID) -> PaymentAssociationRM:
        hits = list(filter(lambda association: association.payment_id == payment_id, self.get_all()))

        if (len(hits) == 0):
            raise ValueError("there is no such element")
        if (len(hits) != 1):
            raise ValueError("duplicates found, data corrupted")
        return hits[0]

    # TODO list comprehension would be slightly better
    def get_by_associated_id(self, id: Id) -> PaymentAssociationRM:
        hits = list(filter(lambda association: association.has_id(id), self.get_all()))

        if (len(hits) == 0):
            raise ValueError("there is no such element")
        if (len(hits) != 1):
            raise ValueError("duplicates found, data corrupted")
        return hits[0]
