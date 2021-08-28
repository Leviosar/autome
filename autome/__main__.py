from autome.state import State
from autome.machine import Machine

if __name__ == "__main__":
    states = [State(f"q{i}", f"q{i}", initial=True) for i in range(10)]
    machine = Machine(states=states)
