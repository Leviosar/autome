from autome.automatas.finite_automata.state import State
from typing import Callable, Dict, List


class Transition:
    """
    A transition between two states in a Finite Automata. Any Transition has an origin state, a
    destiny origin and a trigger symbol.
    """

    def __init__(
        self,
        origin: State,
        destiny: State,
        symbol: str,
    ) -> None:
        self.origin = origin
        self.destiny = destiny
        self.symbol = symbol

    def __repr__(self):
        return f"Transition({self.origin.name} → {self.destiny.name}) : {self.symbol}"

    @classmethod
    def parse(cls, model: dict, states: List[State]) -> "Transition":
        """
        Returns a new instance of Transition based on the contents of @model. This function was written to be used within Machine.parse
        """
        find_origin: Callable[[State], str] = lambda state: state.uid == model["origin"]
        origin = next(filter(find_origin, states))

        find_destiny: Callable[[State], str] = (
            lambda state: state.uid == model["destiny"]
        )
        destiny = next(filter(find_destiny, states))

        return Transition(origin, destiny, model["symbol"])

    def to_json(self) -> Dict:
        return {
            "origin": self.origin.uid,
            "destiny": self.destiny.uid,
            "symbol": self.symbol,
        }

    @classmethod
    def from_json(cls, model: Dict, states: List[State]) -> "Transition":
        find_origin: Callable[[State], str] = lambda state: state.uid == model["origin"]
        origin = next(filter(find_origin, states))

        find_destiny: Callable[[State], str] = (
            lambda state: state.uid == model["destiny"]
        )
        destiny = next(filter(find_destiny, states))

        return Transition(origin, destiny, model["symbol"])

    def __eq__(self, other):
        return (
            self.origin == other.origin
            and self.destiny == other.destiny
            and self.symbol == other.symbol
        )

    def __hash__(self) -> int:
        concat = f"{self.destiny.__hash__()}.{self.origin.__hash__()}.{self.symbol.__hash__()}"
        return hash(concat)
