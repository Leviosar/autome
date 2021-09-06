from autome.machine import Machine
from pathlib import Path
from autome.parsers import JFlapConverter


def test_jff_parsing():
    """
    Test case for converting a .jff (JFlap's default format) file into a Turing Machine. This feature of conversion will be useful 
    while i can't develop a GUI to create machines.
    """
    machine = JFlapConverter.parse(source=Path("./machines/machine.jff"))

    assert isinstance(machine, Machine)
    assert machine.accepts(["abbaab"])
    assert machine.accepts(["aabbaaaab"])
    assert not machine.accepts(["ababab"])