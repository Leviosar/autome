from autome.automatas import NDFA
from autome.regex.nodes import ParserNode


class Interpreter:
    def run(self, node: ParserNode) -> NDFA:
        return node.apply()
