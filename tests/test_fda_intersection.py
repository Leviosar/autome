from pathlib import Path
from autome.finite_automata import (
    JFlapConverter,
    DeterministicFiniteAutomata,
    JSONConverter,
)


def test_fda_intersection():
    return

    """
    Test case for converting a .jff (JFlap's default format) file into a Turing Machine. This feature of conversion will be useful
    while i can't develop a GUI to create machines.
    """
    first_machine = JSONConverter.parse(source=Path("./machines/01-machine.json"))

    assert isinstance(first_machine, DeterministicFiniteAutomata)

    # First we are testing 01-machine by itself
    assert first_machine.accepts("01")
    assert first_machine.accepts("0000000000000001")
    assert not first_machine.accepts("0000000000000011")
    assert not first_machine.accepts("1")
    assert not first_machine.accepts("0")
    assert not first_machine.accepts("10")
    assert not first_machine.accepts("")
    assert first_machine.accepts("101")

    second_machine = JSONConverter.parse(source=Path("./machines/even-1-machine.json"))

    assert isinstance(second_machine, DeterministicFiniteAutomata)

    # Now we test if even-1 machine works
    assert second_machine.accepts("")
    assert second_machine.accepts("11")
    assert second_machine.accepts("110")
    assert second_machine.accepts("11000000000")
    assert second_machine.accepts("11000010010")
    assert second_machine.accepts("00")
    assert not second_machine.accepts("001")
    assert not second_machine.accepts("11001")
    assert not second_machine.accepts("1111001")

    intersection = first_machine & second_machine

    assert isinstance(intersection, DeterministicFiniteAutomata)
    assert not intersection.accepts("11")
    assert not intersection.accepts("0000000000000001")
    assert intersection.accepts("00001000000000001")
    assert not intersection.accepts("")
    assert not intersection.accepts("00")
