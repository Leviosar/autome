from autome.regular_expression.blocks import SymbolAutomata


def test_symbol_automata():
    """
    Test case for converting a .jff (JFlap's default format) file into a Turing Machine. This feature of conversion will be useful
    while i can't develop a GUI to create machines.
    """
    machine = SymbolAutomata("a")

    assert machine.accepts("a")

    assert not machine.accepts("aa")
    assert not machine.accepts("b")
    assert not machine.accepts("")
    assert not machine.accepts("&")
