from __future__ import annotations

from dataclasses import dataclass
from typing import List, Set, Tuple

AssociationType = str
PaymentID = str
Id = str


@dataclass(frozen=True)
class PaymentAssociationRM:
    payment_id: PaymentID
    associations: Set[Tuple[Id, AssociationType]]

    def add_association(self, association: Tuple[Id, AssociationType]) -> PaymentAssociationRM:
        return PaymentAssociationRM(self.payment_id, self.associations.union([association]))

    def has_id(self, id: Id) -> bool:
        return bool([a_id for a_id, _ in self.associations if a_id == id])

    def find_association(self, type: AssociationType) -> List[Id]:
        return [a_id for a_id, a_type in self.associations if a_type == type]
