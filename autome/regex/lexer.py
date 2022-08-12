from enum import Enum
from dataclasses import dataclass
from typing import List

WHITESPACE = " \n\t"


class TokenType(Enum):
    KLEENE_CLOSURE = 0
    POSITIVE_CLOSURE = 1
    LEFT_PARENTHESIS = 2
    RIGHT_PARENTHESIS = 3
    CONCATENATION = 4
    UNION = 5
    SYMBOL = 6


@dataclass
class Token:
    type: TokenType
    value: any = None

    def __repr__(self):
        return self.type.name + (f":{self.value}" if self.value != None else "")


class Lexer:
    def __init__(self, expression) -> None:
        self.expression = iter(expression)
        self.title = self.forward()

    def forward(self):
        try:
            self.current_char = next(self.expression)
        except StopIteration:
            self.current_char = None

    def generate_tokens(self) -> List[Token]:
        while self.current_char != None:
            if self.current_char in WHITESPACE:
                self.forward()
                yield Token(TokenType.CONCATENATION)
            elif self.current_char == "⁺":
                self.forward()
                yield Token(TokenType.POSITIVE_CLOSURE)
            elif self.current_char == "*":
                self.forward()
                yield Token(TokenType.KLEENE_CLOSURE)
            elif self.current_char == "|":
                self.forward()
                yield Token(TokenType.UNION)
            elif self.current_char == "(":
                self.forward()
                yield Token(TokenType.LEFT_PARENTHESIS)
            elif self.current_char == ")":
                self.forward()
                yield Token(TokenType.RIGHT_PARENTHESIS)
            elif self.current_char ==  "\\":
                self.forward()
                yield Token(TokenType.SYMBOL, self.current_char)
                self.forward()
            else:
                yield Token(TokenType.SYMBOL, self.current_char)
                self.forward()
