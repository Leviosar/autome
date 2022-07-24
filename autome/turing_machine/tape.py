import json
from autome.utils.enums import Direction


class Tape:
    """
    Computational representation of an infinite tape of memory
    Cause there's no such thing as infinite memory we're using a statically sized list with a pointer
    Tapes may only contain a single char for position, so any input passed as @initial_value will be splitted that way.
    """

    def __init__(self, initial_value: str = "", pointer: int = 0):
        self.pointer = pointer
        self.data = list(initial_value)

    def __repr__(self):
        return "  " + " " * (self.pointer * 5) + "↓\n" + json.dumps(self.data)

    def __len__(self):
        return len(self.data)

    @classmethod
    def parse(cls, model: dict) -> "Tape":
        """
        Returns a new instance of Tape based on the contents of @model. This function was written to be used within Machine.parse
        """
        return Tape(initial_value=model["initial_string"])

    def get(self):
        """
        Returns the content of the tape at the pointer's position
        """
        if self.pointer < 0 or self.pointer >= len(self):
            return "_"
        else:
            return self.data[self.pointer]

    def write(self, value: str):
        """
        Writes the content passed in @value to the tape at the pointer's position
        """
        if self.pointer < len(self):
            self.data[self.pointer] = value
        else:
            self.data.append(value)

    def move(self, direction: Direction):
        """
        Moves the pointer to the left or the right
        """
        if direction == Direction.LEFT:
            self.pointer -= 1
        elif direction == Direction.RIGHT:
            self.pointer += 1

    def clone(self) -> "Tape":
        """
        Returns a clone of the calling tape
        """
        return Tape("".join(self.data), pointer=self.pointer)
