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
