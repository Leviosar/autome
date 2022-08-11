from autome.automatas.turing_machine.state import State
from autome.automatas.turing_machine.tape import Tape
from autome.automatas.turing_machine.transition import Transition
from typing import List, Callable, Deque
from pathlib import Path
from collections import deque
import json


class Machine:
    """
    Multitape deterministic Turing-Machine, accepts states, tapes and transitions as inputs.

    Outputs boolean for result upon transition to acceptance state or reject state.

    A machine can only have one initial state, but it may have multiple acceptance and reject states. Computation will be stopped as soon as the machine reaches one of those two types of state.
    """

    def __init__(
        self, states=[], tapes=[], transitions=[], branches: Deque = None
    ) -> None:
        self.tapes: List[Tape] = tapes
        self.states: List[State] = states
        self.current_state = next(filter(lambda state: state.initial, self.states))
        self.transitions: List[Transition] = transitions
        self.output = False

        if branches is not None:
            self.branches = branches
        else:
            self.branches: Deque[Machine] = deque([self])

    def __repr__(self):
        return f"Machine(states: {len(self.states)}, tapes: {len(self.tapes)})"

    @classmethod
    def parse(cls, path: Path) -> "Machine":
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

        return Machine(states=states, tapes=tapes, transitions=transitions)

    def clone(self) -> "Machine":
        """
        Returns a clone of the calling Turing Machine. The states, transitions and branches will be shallow copies
        while the tapes are clones with differente memory spaces.

        States and Transitions are read-only, so a shallow copy is fine.

        Tapes have write and move operations, so they must be new objects on the new machine.

        The branches must be shared between instances (we call it a "gambiarra")
        """
        tapes = [tape.clone() for tape in self.tapes]

        return Machine(
            states=self.states,
            tapes=tapes,
            transitions=self.transitions,
            branches=self.branches,
        )

    def execute_transition(self, transition: Transition) -> "Machine":
        """
        Executes a transition into the machine, writing and moving the tapes to apply changes.
        """
        for i in range(len(self.tapes)):
            self.tapes[i].write(transition.writes[i])
            self.tapes[i].move(transition.moves[i])

        self.current_state = transition.destiny

        return self

    def accepts(self, inputs: List[str], steps=False) -> bool:
        """
        Resets the Turing Machine to an entry state and runs the computation for a list of inputs that will be inserted into
        the machine's tapes.
        """
        self.tapes = [Tape(value) for value in inputs]
        self.current_state = next(filter(lambda state: state.initial, self.states))
        self.branches: Deque[Machine] = deque([self])

        return self.run(steps)

    def run(self, steps=False) -> bool:
        """
        Runs the computation for the current Turing-Machine.
        If @steps is True, computation will run in a step-by-step mode, use this for debug. To control step by step mode, hit Enter on REPL to go to the next step.
        """
        output = False
        while len(self.branches) > 0:
            branch = self.branches.popleft()
            if steps:
                input()
            output = branch.step()
        return output

    def step(self) -> bool:
        """
        Runs one step of the computation for the current Turing-Machine.

        The step will take the current input of all the machine's tapes, compare with the list
        of available transitions trying to find a match. If it doesn't find, the machine will
        be pushed into a rejection state, where the computation will stop.

        However, if it does find a match (and only one, because the machine stils can't handle non-determinism)
        it will apply all the changes requested on tapes, then shifts the current state of the machine
        to the destiny of the found transition.
        """
        symbols = [tape.get() for tape in self.tapes]

        condition: Callable[[Transition], bool] = (
            lambda transition: symbols == transition.reads
            and self.current_state == transition.origin
        )

        matches = list(filter(condition, self.transitions))

        if len(matches) == 0:
            return self.current_state.accept
        else:
            for transition in matches[1:]:
                self.branches.append(self.clone().execute_transition(transition))

            self.branches.append(self.execute_transition(matches[0]))
