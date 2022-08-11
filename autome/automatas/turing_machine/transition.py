from autome.utils.enums import Direction
from autome.automatas.turing_machine.state import State
from typing import Callable, List


class Transition:
    """
    A transition between two states in a Turing-Machine. Any Transition has an origin state, a
    """

    def __init__(
        self,
        origin: State,
        destiny: State,
        reads: List[str],
        writes: List[str],
        moves: List[Direction],
    ) -> None:
        self.origin = origin
        self.destiny = destiny
        self.reads = reads
        self.writes = writes
        self.moves = moves

    def __repr__(self):
        return f"Transition({self.origin.label} → {self.destiny.label}) : {self.reads} → {self.writes}"

    @classmethod
    def parse(cls, model: dict, states: List[State]) -> "Transition":
        """
        Returns a new instance of Transition based on the contents of @model. This function was written to be used within Machine.parse
        """
        find_origin: Callable[[State], str] = (
            lambda state: state.name == model["origin"]
        )
        origin = next(filter(find_origin, states))

        find_destiny: Callable[[State], str] = (
            lambda state: state.name == model["destiny"]
        )
        destiny = next(filter(find_destiny, states))

        moves = [Direction[dir.upper()] for dir in model["moves"]]

        return Transition(origin, destiny, model["reads"], model["writes"], moves)
