from autome.utils import Direction
from autome.state import State


class Transition:
    def __init__(self, origin: State, destiny: State, reads: str, writes: str, moves: Direction) -> None:
        self.origin = origin
        self.destiny = destiny
        self.reads = reads
        self.writes = writes
        self.moves = moves
