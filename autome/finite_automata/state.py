from os import stat
from typing import Dict, List
from itertools import count
from time import time
from uuid import uuid4


class State:
    _ids = count(0)

    """
    A possible State of a Finite Automata.
    """

    def __init__(
        self,
        name: str = None,
        initial=False,
        accept=False,
        type=None,
        uid=None,
        parts=[],
    ) -> None:
        self.initial: bool = initial
        self.accept: bool = accept
        self.id = next(self._ids)
        self.type: str = type
        self.parts: List[float] = parts

        if uid is not None:
            self.uid = uid
        else:
            self.uid = str(uuid4())

        if name is None:
            self.name = f"q{self.id}"
        else:
            self.name: str = name

    @classmethod
    def parse(cls, model: dict) -> "State":
        """
        Returns a new instance of State based on the contents of @model. This function was written to be used within Machine.parse
        """
        return State(
            model.get("name"),
            initial=model.get("initial"),
            accept=model.get("accept"),
            uid=model.get("uid"),
        )

    def to_json(self) -> Dict:
        return {
            "name": self.name,
            "initial": self.initial,
            "accept": self.accept,
            "uid": self.uid,
            "type": self.type,
        }

    @classmethod
    def from_json(cls, model: Dict) -> "State":
        return State(
            initial=model.get("initial"),
            accept=model.get("accept"),
            uid=model.get("uid"),
            type=model.get("type"),
        )

    @classmethod
    def join(cls, states: List["State"]) -> "State":
        if len(states) == 1:
            return states[0]

        parts = list(map(lambda state: str(state.uid), states))
        parts.sort()

        names = list(map(lambda state: state.name, states))
        names.sort()
        name = ".".join(names)

        accept = len(list(filter(lambda state: state.accept, states))) > 0
        initial = len(list(filter(lambda state: state.initial, states))) > 0
        types = set(map(lambda state: state.type, states))
        types = list(filter(lambda t: t is not None, types))

        if len(types) > 0:
            type = types[0]
        else:
            type = None

        return State(name=name, accept=accept, initial=initial, type=type, parts=parts)

    def debug(self):
        return f"{self.name} ({self.type})"

    def __repr__(self):
        return f"q{self.id}"
        # return f"State(id: {self.name}, accept: {self.accept}, initial: {self.initial}, type: {self.type})"

    def __lt__(self, other: "State") -> bool:
        return self.name < other.name

    def __eq__(self, other):
        if type(other) != State:
            return False

        # Problema: criar uma forma de identificação para estados que atenda os requisitos:
        #   - O identificador deve ser globalmente único, para permitir save/parse
        #   - Ao criar estados com State.join(), sempre que fizer join(a,b,c) o estado resultante deve possuir o mesmo identificador

        # if (len(self.parts) > 0 and len(other.parts) > 0):
        # print(self.parts)
        # print(other.parts)
        # print(self.parts == other.parts)
        # return self.parts == other.parts

        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)
