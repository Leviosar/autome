from pathlib import Path
from autome.automatas.finite_automata import (
    JFlapConverter,
    JSONConverter,
    DeterministicFiniteAutomata,
    State,
    Transition,
)


def test_dfa_parsing():
    """
    Test case for converting a .jff (JFlap's default format) and .json (this project's schema) files into a FDAs.
    """
    a = json()
    b = expected()

    assert isinstance(a, DeterministicFiniteAutomata)
    assert isinstance(b, DeterministicFiniteAutomata)
    assert a.accepts("abab") == b.accepts("abab")
    assert a.accepts("aaabba") == b.accepts("aaabba")
    assert a.accepts("a") == b.accepts("a")
    assert a.accepts("bb") == b.accepts("bb")
    assert a.accepts("ba") == b.accepts("ba")
    assert a.accepts("") == b.accepts("")
    assert a.accepts("ababbaa") == b.accepts("ababbaa")


def json() -> DeterministicFiniteAutomata:
    return JSONConverter.parse(source=Path("./machines/cross-machine.json"))


def jff() -> DeterministicFiniteAutomata:
    return JFlapConverter.parse(source=Path("./machines/cross-machine.jff"))


def expected() -> DeterministicFiniteAutomata:
    states = [
        State("0", initial=True, uid="0"),
        State("1", uid="1"),
        State("2", accept=True, uid="2"),
    ]

    transitions = [
        Transition(states[0], states[1], "a"),
        Transition(states[0], states[2], "a"),
        Transition(states[1], states[2], "b"),
        Transition(states[2], states[0], "&"),
    ]

    return DeterministicFiniteAutomata(states=states, transitions=transitions)
