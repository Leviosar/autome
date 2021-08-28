from autome import Machine, State, Tape, Transition
from autome.utils import Direction


def test_copy_machine():
    """
    Test case for a Turing-Machine capable of copying the input given on tape A to tape B.
    """
    states = [
        State("q0", "q0", initial=True),
        State("q1", "q1", accept=True),
    ]

    tapes = [Tape("aaabbb"), Tape()]

    transitions = [
        Transition(
            states[0],
            states[0],
            ["a", "_"],
            ["A", "a"],
            [Direction.RIGHT, Direction.RIGHT],
        ),
        Transition(
            states[0],
            states[0],
            ["b", "_"],
            ["B", "b"],
            [Direction.RIGHT, Direction.RIGHT],
        ),
        Transition(
            states[0],
            states[1],
            ["_", "_"],
            ["_", "_"],
            [Direction.STAY, Direction.STAY],
        ),
    ]

    machine = Machine(states=states, tapes=tapes, transitions=transitions)

    assert machine.run()
