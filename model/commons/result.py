from abc import ABC


class Result(ABC):
    __details = NotImplemented

    def __init__(self, details=""):
        self.__details = details

    @property
    def details(self):
        return self.__details

    def succeded(self) -> bool:
        return True

    def failed(self) -> bool:
        return not self.succeded()


class Success(Result):
    pass


class Fail(Result):
    def succeded(self) -> bool:
        return False
