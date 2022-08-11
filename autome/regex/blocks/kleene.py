from autome.automatas.finite_automata.machine import (
    NonDeterministicFiniteAutomata,
)
from autome.automatas.finite_automata.state import State
from autome.automatas.finite_automata.transition import Transition


class KleeneAutomata(NonDeterministicFiniteAutomata):
    """Creates a concatenation recognizer automata, which accepts the Kleene closure of the languages regognized by its inputs.

    Args:
        a (NonDeterministicFiniteAutomata): first operand.
    """

    def __init__(self, a: NonDeterministicFiniteAutomata) -> "KleeneAutomata":
        # Using deep copys to avoid modifying the original automata.
        temp_a = a.clone()

        # Creating new initial and final state
        new_initial = State(initial=True)
        new_final = State(accept=True)

        new_transitions = []

        # Creating epsilon transitions between the new initial and old initial states
        new_transitions.append(Transition(new_initial, new_final, "&"))
        new_transitions.append(Transition(new_initial, temp_a.initial(), "&"))

        # For each final state we should create epsilon transitions to the old initial state and to the new final state
        for state in temp_a.final():
            new_transitions.append(Transition(state, temp_a.initial(), "&"))
            new_transitions.append(Transition(state, new_final, "&"))
            state.accept = False

        # Marking old initial states as non-initial
        temp_a.initial().initial = False

        states = temp_a.states + [new_initial, new_final]
        transitions = temp_a.transitions + new_transitions

        super().__init__(states, transitions)
