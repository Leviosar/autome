from autome.automatas.finite_automata.machine import (
    NonDeterministicFiniteAutomata,
)
from autome.automatas.finite_automata.state import State
from autome.automatas.finite_automata.transition import Transition


class UnionAutomata(NonDeterministicFiniteAutomata):
    """Creates a concatenation recognizer automata, which accepts the union of the languages regognized by its inputs.

    Args:
        a (NonDeterministicFiniteAutomata): first operand.
        b (NonDeterministicFiniteAutomata): second operand.
    """

    def __init__(
        self, a: NonDeterministicFiniteAutomata, b: NonDeterministicFiniteAutomata
    ) -> "UnionAutomata":
        # Using deep copys to avoid modifying the original automata.
        temp_a = a.clone()
        temp_b = b.clone()

        # Creating new initial and final state
        new_initial = State(initial=True)
        new_final = State(accept=True)

        new_transitions = []

        # Creating epsilon transitions between the new initial and old initial states
        new_transitions.append(Transition(new_initial, temp_a.initial(), "&"))
        new_transitions.append(Transition(new_initial, temp_b.initial(), "&"))

        # Marking old initial states as non-initial
        temp_a.initial().initial = False
        temp_b.initial().initial = False

        # Creating epsilon transitions between the old final states and the new final state
        # Marking old final states as non-final
        for state in temp_a.final():
            state.accept = False
            new_transitions.append(Transition(state, new_final, "&"))

        for state in temp_b.final():
            state.accept = False
            new_transitions.append(Transition(state, new_final, "&"))

        states = temp_a.states + temp_b.states + [new_initial, new_final]
        transitions = temp_a.transitions + temp_b.transitions + new_transitions

        super().__init__(states, transitions)
