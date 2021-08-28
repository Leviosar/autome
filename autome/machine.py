from autome.state import State
from autome.transition import Transition
from typing import List


class Machine:
    def __init__(self, states = [], tapes = [[]]) -> None:
        self.tapes: List[List[str]] = tapes
        self.states: List[State] = states
    
    
    def add_state(self, state: State):
        self.states.append(state)
    

    def add_transition(self, transition: Transition):
        self.transitions.append(transition)