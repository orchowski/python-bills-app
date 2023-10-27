from dataclasses import dataclass
from enum import Enum

from typing import List, Dict


class Lang(Enum):
    EN = "en"
    PL = "pl"


@dataclass(frozen=True)
class Recipients:
    recipients: List[str]


@dataclass(frozen=True)
class MailTemplate:
    template_name: str
    language: Lang
    content: Dict[str, str]


@dataclass(frozen=True)
class Subject:
    subject: str


@dataclass(frozen=True)
class MailMessage:
    recipients: Recipients
    subject: Subject
    template: MailTemplate
