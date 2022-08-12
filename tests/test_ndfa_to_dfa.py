from pathlib import Path
from autome.automatas.finite_automata import (
    JFlapConverter,
    DeterministicFiniteAutomata,
    JSONConverter,
)


def test_ndfa_to_dfa():
    """
    Test case for transforming a NDFA into a DFA using the determinization algorithm
    """
    machine = JSONConverter.parse(
        source=Path("./machines/cross-machine.json"), deterministic=False
    )
    machine = machine.determinize()

    target = expected()

    assert isinstance(machine, DeterministicFiniteAutomata)
    assert isinstance(target, DeterministicFiniteAutomata)

    assert machine.accepts("a") and target.accepts("a")
    assert machine.accepts("ab") and target.accepts("ab")
    assert machine.accepts("aaaaaaaaaaaa") and target.accepts("aaaaaaaaaaaa")
    assert not machine.accepts("abba") and not target.accepts("abba")


def expected() -> DeterministicFiniteAutomata:
    return JSONConverter.parse(Path("./machines/deterministic-cross-machine.json"))
