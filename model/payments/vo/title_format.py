from dataclasses import dataclass
from enum import Enum


class TitleFormatTypes(Enum):
    UNKNOWN = 0
    STATIC = 1


@dataclass(frozen=True)
class TitleFormat:
    format: str
    type: TitleFormatTypes
