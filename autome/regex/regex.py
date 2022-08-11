from autome.automatas import NDFA
from autome.regex import Lexer, Parser, Interpreter


class Regex:
    def __init__(self, expression) -> None:
        self.expression = expression
        self.lexer = Lexer(self.expression)
        self.tokens = self.lexer.generate_tokens()
        self.parser = Parser(self.tokens)
        self.tree = self.parser.parse()
        self.interpreter = Interpreter()

    def match(self, test) -> bool:
        return self.interpreter.run(self.tree).determinize().accepts(test)

    def automata(self) -> NDFA:
        return self.interpreter.run(self.tree)
