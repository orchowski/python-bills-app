from dataclasses import dataclass


@dataclass
class Unit:
    name: str

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, o) -> bool:
        if type(self) == type(o):
            return self.name == o.name
        return False
