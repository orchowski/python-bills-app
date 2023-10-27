from dataclasses import dataclass


@dataclass(frozen=True)
class AccountingDocumentAttachmentDTO:
    document_content: bytes
    file_name: str
