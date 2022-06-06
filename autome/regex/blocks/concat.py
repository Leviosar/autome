from autome.finite_automata.machine import NonDeterministicFiniteAutomata
from autome.finite_automata.state import State
from autome.finite_automata.transition import Transition


class ConcatenationAutomata(NonDeterministicFiniteAutomata):
    """Creates a concatenation recognizer automata, which accepts the concatenations of the languages regognized by its inputs.

    Args:
        a (NonDeterministicFiniteAutomata): first operand.
        b (NonDeterministicFiniteAutomata): second operand.
    """

    def __init__(
        self, a: NonDeterministicFiniteAutomata, b: NonDeterministicFiniteAutomata
    ) -> "ConcatenationAutomata":
        # Using deep copys to avoid modifying the original automata.
        temp_a = a.clone()
        temp_b = b.clone()

        print(temp_a)
        print(temp_b)

        new = []
        # All transitions going from the initial state of the second DFA now should start on the
        # final state of the first DFA

        starting_from_old = lambda transition: transition.origin == temp_b.initial()

        for transition in filter(starting_from_old, temp_b.transitions):
            for state in temp_a.final():
                # Handles the case where a initial state has transitions to itself
                destiny = (
                    transition.destiny
                    if transition.destiny != temp_b.initial()
                    else state
                )
                new.append(Transition(state, transition.destiny, transition.symbol))
            temp_b.transitions.remove(transition)

        # Now we can remove the initial state of the second DFA
        temp_b.states.remove(temp_b.initial())

        # And the final states from the first DFA are no longer final
        for state in temp_a.final():
            # If a initial state is also final, probably is for accepting the empty string
            state.accept = False

        states = temp_a.states + temp_b.states
        transitions = temp_a.transitions + temp_b.transitions + new

        super().__init__(states, transitions)
