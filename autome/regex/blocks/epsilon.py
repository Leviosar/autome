from autome.automatas.finite_automata.machine import NonDeterministicFiniteAutomata
from autome.automatas.finite_automata.state import State
from autome.automatas.finite_automata.transition import Transition


class EpsilonAutomata(NonDeterministicFiniteAutomata):
    """Creates a symbol recognizer automata, which accepts the symbol @symbol.

        The transition table of the automata is:
        | states |   by   |
        | → q0   | symbol |
        | * q1   |   --   |

    Args:
        symbol (string): the symbol to be recognized.
    """

    def __init__(self) -> "EpsilonAutomata":
        states = [State(initial=True), State(accept=True)]
        transitions = [Transition(states[0], states[1], "&")]
        title = f"Reconhecedor da ER: &"
        super().__init__(states, transitions, title)
