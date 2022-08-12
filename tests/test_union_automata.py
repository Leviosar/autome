from autome.regex.blocks import SymbolAutomata, UnionAutomata


def test_union_automata():
    """Test case for building union automatas from symbol automatas"""
    a = SymbolAutomata("a")
    b = SymbolAutomata("b")

    machine = UnionAutomata(a, b).determinize()

    assert machine.accepts("a")
    assert machine.accepts("b")

    assert not machine.accepts("ab")
    assert not machine.accepts("ba")
    assert not machine.accepts("")
    assert not machine.accepts("&")
