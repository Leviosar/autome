from autome.regex.blocks import (
    SymbolAutomata,
    KleeneAutomata,
    ConcatenationAutomata,
)


def test_kleene_automata():
    """
    Test case for creating a kleene closure automata from a symbol automata
    """
    a = SymbolAutomata("a")

    machine = KleeneAutomata(a).determinize()

    assert machine.accepts("aa")
    assert machine.accepts("a")
    assert machine.accepts("aaaa")
    assert machine.accepts("")

    assert not machine.accepts("aaaaab")
    assert not machine.accepts("baaaaa")
