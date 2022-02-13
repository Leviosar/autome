from pathlib import Path
from autome.finite_automata import JFlapConverter, JSONConverter, DeterministicFiniteAutomata, State, Transition


def test_jff_parsing():
    """
    Test case for converting a .jff (JFlap's default format) and .json (this project's schema) files into a FDAs. 
    """
    assert isinstance(json(), DeterministicFiniteAutomata)
    assert isinstance(jff(), DeterministicFiniteAutomata)
    assert isinstance(expected(), DeterministicFiniteAutomata)
    
    assert json() == expected()
    assert jff() == expected()
    assert json() == jff()
    
def json() -> DeterministicFiniteAutomata:
    return JSONConverter.parse(source=Path("./machines/cross-machine.json"))
    
def jff() -> DeterministicFiniteAutomata:
    return JFlapConverter.parse(source=Path("./machines/cross-machine.jff"))
    
def expected() -> DeterministicFiniteAutomata:
    states = [
        State('0', initial=True),
        State('1'),
        State('2', accept=True),
    ]
    
    transitions = [
        Transition(states[0], states[1], 'a'),
        Transition(states[0], states[2], 'a'),
        Transition(states[1], states[2], 'b'),
        Transition(states[2], states[0], '&'),
    ]
    
    return DeterministicFiniteAutomata(states=states, transitions=transitions)