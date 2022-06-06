from autome.regular_expression import Lexer, Parser, Interpreter

class Regex:
    def __init__(self, expression) -> None:
        self.expression = expression
        self.lexer = Lexer(self.expression)
        self.tokens = self.lexer.generate_tokens()
        self.parser = Parser(self.tokens)
        self.tree = self.parser.parse()
        self.interpreter = Interpreter()
            
    def match(self, test) -> bool:
        return self.interpreter.run(self.tree).accepts(test)