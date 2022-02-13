from typing import List


class State:
    """
    A possible State of a Finite Automata.
    """

    def __init__(self, name: str, initial=False, accept=False) -> None:
        self.name = name
        self.initial = initial
        self.accept = accept

    @classmethod
    def parse(cls, model: dict) -> "State":
        """
        Returns a new instance of State based on the contents of @model. This function was written to be used within Machine.parse
        """
        return State(
            model["label"],
            model["name"],
            initial=model["initial"],
            accept=model["accept"],
            reject=model["reject"],
        )

    def __repr__(self):
        return f"State(label: {self.label}, accept: {self.accept}, reject: {self.reject}, initial: {self.initial})"

    def __eq__(self, other):
        return self.name == other.name
