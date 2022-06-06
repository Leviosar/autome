from autome.finite_automata.machine import NonDeterministicFiniteAutomata
from autome.regex.nodes import ParserNode


class Interpreter:
    def run(self, node: ParserNode) -> NonDeterministicFiniteAutomata:
        return node.apply()
