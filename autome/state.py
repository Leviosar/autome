from typing import List


class State:
    """
    A possible State of a Turing-Machine.
    """

    def __init__(
        self, label: str, name: str, initial=False, accept=False, reject=False
    ) -> None:
        self.label = label
        self.name = name
        self.initial = initial
        self.accept = accept
        self.reject = reject

    def __repr__(self):
        return (
            f"State(label: {self.label}, accept: {self.accept}, reject: {self.reject})"
        )
