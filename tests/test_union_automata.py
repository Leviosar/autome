from autome.regex.blocks import SymbolAutomata, UnionAutomata


def test_union_automata():
    """
    Test case for converting a .jff (JFlap's default format) file into a Turing Machine. This feature of conversion will be useful
    while i can't develop a GUI to create machines.
    """
    a = SymbolAutomata("a")
    b = SymbolAutomata("b")

    machine = UnionAutomata(a, b).determinize()

    assert machine.accepts("a")
    assert machine.accepts("b")

    assert not machine.accepts("ab")
    assert not machine.accepts("ba")
    assert not machine.accepts("")
    assert not machine.accepts("&")
