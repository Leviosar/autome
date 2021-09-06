from autome.machine import Machine
from pathlib import Path
from autome.parsers import JFlapConverter


def test_non_deterministic_machine():
    """
    Test case for a non deterministic Turing-Machine capable of identifying the language {w !w w}.
    """

    machine = JFlapConverter.parse(source=Path("./machines/machine.jff"))

    assert isinstance(machine, Machine)
    assert machine.accepts(["abbaab"])
    assert machine.accepts(["aabbaaaab"])
    assert machine.accepts(["aaa"])
    assert machine.accepts(["bbb"])
    assert not machine.accepts(["ababab"])
    assert not machine.accepts(["a"])
    assert not machine.accepts(["b"])