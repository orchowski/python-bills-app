from dataclasses import dataclass


@dataclass(frozen=True)
class TransferRecipientData:
    id: str
    name: str
    iban: str
