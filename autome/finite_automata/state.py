from os import stat
from typing import List
from itertools import count
import uuid


class State:
    _ids = count(0)

    """
    A possible State of a Finite Automata.
    """

    def __init__(self, name: str, initial=False, accept=False) -> None:
        self.id: str = id
        self.name: str = name
        self.initial: bool = initial
        self.accept: bool = accept
        self.id = next(self._ids)

    @classmethod
    def parse(cls, model: dict) -> "State":
        """
        Returns a new instance of State based on the contents of @model. This function was written to be used within Machine.parse
        """
        return State(
            model["name"],
            initial=model["initial"],
            accept=model["accept"],
        )

    @classmethod
    def join(cls, states: List["State"]) -> "State":
        if len(states) == 1:
            return states[0]

        names = list(map(lambda state: state.name, states))
        names.sort()
        name = ".".join(names)
        accept = len(list(filter(lambda state: state.accept, states))) > 0
        initial = len(list(filter(lambda state: state.initial, states))) > 0

        return State(name=name, accept=accept, initial=initial)

    def __repr__(self):
        return self.name
        return f"State(id: {self.name}, accept: {self.accept}, initial: {self.initial})"

    def __lt__(self, other: "State") -> bool:
        return self.name < other.name

    def __eq__(self, other):
        if type(other) != State:
            return False

        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)
