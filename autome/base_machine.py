from autome.automatas.turing_machine.state import State
from autome.automatas.turing_machine.tape import Tape
from autome.automatas.turing_machine.transition import Transition
from typing import List, Callable, Deque
from pathlib import Path
from collections import deque
import json


class BaseMachine:
    """
    Generic machine, accepts states, tapes and transitions as inputs.

    Outputs boolean for result upon transition to acceptance state or reject state.

    A machine can only have one initial state, but it may have multiple acceptance and reject states. Computation will be stopped as soon as the machine reaches one of those two types of state.
    """

    def __init__(
        self, states=[], tapes=[], transitions=[], branches: Deque = None
    ) -> None:
        self.states: List[State] = states
        self.current_state = next(filter(lambda state: state.initial, self.states))
        self.transitions: List[Transition] = transitions
        self.output = False

        if branches is not None:
            self.branches = branches
        else:
            self.branches: Deque[BaseMachine] = deque([self])

    def __repr__(self):
        return f"BaseMachine(states: {len(self.states)})"

    @classmethod
    def parse(cls, path: Path) -> "BaseMachine":
        """
        Creates an instance of Machine parsed from a json file located at @path that follows the schematics provided by the project (see /machines folder)

        Throws FileNotFoundError if there's no file at @path
        Throws ValueError if the json file doesn't match the schematics
        """
        with open(path, "r", encoding="utf8") as file:
            model = json.loads(file.read())
            tapes = [Tape.parse(tape) for tape in model["tapes"]]
            states = [State.parse(state) for state in model["states"]]
            transitions = [
                Transition.parse(transition, states)
                for transition in model["transitions"]
            ]

        return BaseMachine(states=states, tapes=tapes, transitions=transitions)

    def clone(self) -> "BaseMachine":
        """
        Returns a clone of the calling Turing Machine. The states, transitions and branches will be shallow copies
        while the tapes are clones with differente memory spaces.

        States and Transitions are read-only, so a shallow copy is fine.

        Tapes have write and move operations, so they must be new objects on the new machine.

        The branches must be shared between instances (we call it a "gambiarra")
        """
        tapes = [tape.clone() for tape in self.tapes]

        return BaseMachine(
            states=self.states,
            tapes=tapes,
            transitions=self.transitions,
            branches=self.branches,
        )
