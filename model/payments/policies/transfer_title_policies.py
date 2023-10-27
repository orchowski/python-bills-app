from abc import ABC, abstractmethod


class TransferTitleGenerationPolicy(ABC):
    format: str

    def __init__(self, format: str):
        self.format = format

    @abstractmethod
    def generate(self, **kwargs) -> str:
        pass


class StaticTitlePolicy(TransferTitleGenerationPolicy):
    def generate(self, **kwargs) -> str:
        return self.format
