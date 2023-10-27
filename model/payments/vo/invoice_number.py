from dataclasses import dataclass


@dataclass(frozen=True)
class InvoiceNumber:
    number: str

    def __post_init__(self):
        if len(self.number.strip()) < 5:
            raise ValueError("incorrect invoice number")

    def __str__(self) -> str:
        return self.number
