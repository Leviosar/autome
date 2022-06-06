from autome.regex.blocks import (
    SymbolAutomata,
    KleeneAutomata,
    ConcatenationAutomata,
)


def test_kleene_automata():
    """
    Test case for converting a .jff (JFlap's default format) file into a Turing Machine. This feature of conversion will be useful
    while i can't develop a GUI to create machines.
    """
    a = SymbolAutomata("a")
    b = SymbolAutomata("b")

    machine = KleeneAutomata(a).determinize()

    assert machine.accepts("aa")
    assert machine.accepts("aaaa")
    assert machine.accepts("")

    assert not machine.accepts("aaaaab")
    assert not machine.accepts("baaaaa")

    temp = ConcatenationAutomata(a, b)
    machine = KleeneAutomata(temp).determinize()

    assert machine.accepts("abababab")
    assert machine.accepts("abab")
    assert not machine.accepts("aabab")
    assert not machine.accepts("bababa")
