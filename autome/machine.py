from autome.state import State
from autome.transition import Transition
from typing import List


class Machine:
    """
    Multitape deterministic Turing-Machine, accepts states, tapes and transitions as inputs.

    Outputs boolean for result upon transition to acceptance state or reject state.

    A machine can only have one initial state, but it may have multiple acceptance and reject states. Computation will be stopped as soon as the machine reaches one of those two types of state.
    """

    def __init__(self, states=[], tapes=[], transitions=[]) -> None:
        self.tapes: List[Tape] = tapes
        self.states: List[State] = states
        self.current_state = next(filter(lambda state: state.initial, self.states))
        self.transitions: List[Transition] = transitions
        self.output = False

    def __repr__(self):
        return f"Machine(states: {len(self.states)}, tapes: {len(self.tapes)})"

    def run(self, steps=False):
        """
        Runs the computation for the current Turing-Machine.
        If @steps is True, computation will run in a step-by-step mode, use this for debug. To control step by step mode, hit Enter on REPL to go to the next step.
        """
        while not (self.current_state.accept or self.current_state.reject):
            if steps:
                input()
            self.step()
        return self.output

    def step(self):
        """
        Runs one step of the computation for the current Turing-Machine.

        The step will take the current input of all the machine's tapes, compare with the list
        of available transitions trying to find a match. If it doesn't find, the machine will
        be pushed into a rejection state, where the computation will stop.

        However, if it does find a match (and only one, because the machine stils can't handle non-determinism)
        it will apply all the changes requested on tapes, then shifts the current state of the machine
        to the destiny of the found transition.
        """
        if not (self.current_state.accept or self.current_state.reject):
            symbols = [tape.get() for tape in self.tapes]

            matches = list(
                filter(lambda transition: symbols == transition.reads, self.transitions)
            )

            if len(matches) == 0:
                self.current_state = State("qr", "qr", reject=True)
            elif len(matches) > 1:
                raise Exception(
                    "Non-deterministic transition, you're breaking the rules of time and space."
                )
            else:
                transition = matches[0]

                for i in range(len(self.tapes)):
                    self.tapes[i].write(transition.writes[i])
                    self.tapes[i].move(transition.moves[i])

                self.current_state = transition.destiny

                if self.current_state.reject or self.current_state.accept:
                    self.output = self.current_state.accept
        else:
            self.output = self.current_state.accept
