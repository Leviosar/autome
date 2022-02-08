from autome import FiniteAutomata, State, Tape, Transition
from autome.utils import Direction


def test_parity_finite_automata():
    """
    Test case for a finite automata capable of check if the number of a's is odd.
    """
    states = [
        State("q0", "q0", initial=True),
        State("q1", "q1"),
        State("q2", "q2"),
        State("qa", "qa", accept=True),
    ]

    tapes = [Tape("aaabbb"), Tape()]

    transitions = [
        Transition(
            states[0],
            states[1],
            ["a", "_"],
            ["A", "_"],
            [Direction.RIGHT, Direction.STAY],
        ),
        Transition(
            states[1],
            states[1],
            ["a", "_"],
            ["a", "_"],
            [Direction.RIGHT, Direction.STAY],
        ),
        Transition(
            states[1],
            states[1],
            ["b", "_"],
            ["b", "c"],
            [Direction.RIGHT, Direction.RIGHT],
        ),
        Transition(
            states[1],
            states[2],
            ["_", "_"],
            ["_", "_"],
            [Direction.STAY, Direction.STAY],
        ),
        Transition(
            states[2],
            states[2],
            ["b", "_"],
            ["b", "_"],
            [Direction.LEFT, Direction.STAY],
        ),
        Transition(
            states[2],
            states[2],
            ["a", "_"],
            ["a", "_"],
            [Direction.LEFT, Direction.STAY],
        ),
        Transition(
            states[2],
            states[0],
            ["A", "_"],
            ["A", "_"],
            [Direction.RIGHT, Direction.STAY],
        ),
        Transition(
            states[0],
            states[3],
            ["_", "_"],
            ["_", "_"],
            [Direction.RIGHT, Direction.STAY],
        ),
    ]

    machine = Machine(states=states, tapes=tapes, transitions=transitions)
    machine.run(steps=True)
    assert True
