from autome.regex.blocks import SymbolAutomata


def test_symbol_automata():
    """Test case for building symbol automatas"""
    machine = SymbolAutomata("a")

    assert machine.accepts("a")

    assert not machine.accepts("aa")
    assert not machine.accepts("b")
    assert not machine.accepts("")
    assert not machine.accepts("&")
