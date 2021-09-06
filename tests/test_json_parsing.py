from autome.machine import Machine
from pathlib import Path

def test_json_parsing():
    """
    Test case for a dummy Turing-Machine parsed via JSON file.
    """

    machine = Machine.parse(Path("./machines/copy_machine.json"))

    assert isinstance(machine, Machine)
    assert machine.accepts(["ababab", ""])