# from autome.regex.symbol_automata import SymbolAutomata
# from autome.regex.concatenation_automata import ConcatenationAutomata

from autome.regex.blocks import SymbolAutomata, ConcatenationAutomata
from autome.regex.blocks.kleene import KleeneAutomata


def test_concatenation_automata():
    """
    Test case for converting a .jff (JFlap's default format) file into a Turing Machine. This feature of conversion will be useful
    while i can't develop a GUI to create machines.
    """
    a = SymbolAutomata("a")
    b = SymbolAutomata("b")
    c = SymbolAutomata("c")

    # Testing simple concatenation
    machine = ConcatenationAutomata(a, b)
    # assert machine.accepts("ab")
    # assert not machine.accepts("aab")
    # assert not machine.accepts("ba")
    # assert not machine.accepts("b")
    # assert not machine.accepts("a")
    # assert not machine.accepts("")
    # assert not machine.accepts("&")

    # Testing compound concatenation
    machine = ConcatenationAutomata(machine, c)
    trick = KleeneAutomata(c)
    machine = ConcatenationAutomata(machine, trick)

    assert machine.accepts("abc")
    assert not machine.accepts("aab")
    assert not machine.accepts("bac")
    assert not machine.accepts("b")
    assert not machine.accepts("a")
    assert not machine.accepts("c")
    assert not machine.accepts("")
    assert not machine.accepts("&")

    # Testing self concatenation
    # machine = ConcatenationAutomata(a, a)
    # assert machine.accepts("aa")
    # assert not machine.accepts("aab")
    # assert not machine.accepts("bac")
    # assert not machine.accepts("b")
    # assert not machine.accepts("a")
    # assert not machine.accepts("c")
    # assert not machine.accepts("")
    # assert not machine.accepts("&")
