from autome.utils import Direction
from autome.state import State
from typing import List


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
        return f"Transition({self.origin.label} → {self.destiny.label})"
