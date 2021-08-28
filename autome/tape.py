import json
from autome.utils import Direction


class Tape:
    """
    Computational representation of an infinite tape of memory
    Cause there's no such thing as infinite memory we're using a statically sized list with a pointer
    Tapes may only contain a single char for position, so any input passed as @initial_value will be splitted that way.
    """

    def __init__(self, initial_value: str = ""):
        self.pointer = 0
        initial_size = len(list(initial_value))
        self.data = list(initial_value) + (["_"] * (1000 - initial_size))

    def __repr__(self):
        return json.dumps(self.data)

    def get(self):
        """
        Returns the content of the tape at the pointer's position
        """
        return self.data[self.pointer]

    def write(self, value: str):
        """
        Writes the content passed in @value to the tape at the pointer's position
        """
        self.data[self.pointer] = value

    def move(self, direction: Direction):
        """
        Moves the pointer to the left or the right
        """
        if direction == Direction.LEFT:
            self.pointer -= 1
        elif direction == Direction.RIGHT:
            self.pointer += 1
