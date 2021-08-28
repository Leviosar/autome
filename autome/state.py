from autome.transition import Transition
from typing import List


class State:
    def __init__(self, label: str, name: str, final = False, initial = False) -> None:
        self.label = label
        self.name = name
        self.final = final
        self.initial = initial
        self.transitions: List[Transition] = []