from dataclasses import dataclass
from typing import Optional
from autome.regex.regex import Regex


@dataclass
class Definition:
    name: str
    expression: str
    regex: Optional[Regex] = None

    def __repr__(self):
        return f"{self.name} => {self.expression}"

    def dict(self):
        return {"name": self.name, "expression": self.expression}


@dataclass
class Token:
    type: str
    value: str

    def __repr__(self) -> str:
        return f"{self.type}:{self.value}"
