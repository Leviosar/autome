from typing import List
from autome.regex import Token, TokenType

from autome.regex.nodes import (
    ConcatNode,
    KleeneClosureNode,
    ParserNode,
    PositiveClosureNode,
    SymbolNode,
    UnionNode,
)


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = iter(tokens)
        self.forward()

    def throw(self) -> None:
        problem = self.current_token
        rest = []

        while self.current_token is not None:
            self.forward()
            rest.append(self.current_token)

        raise Exception(f"Unexpected token {problem} in {rest}")

    def forward(self) -> None:
        try:
            self.current_token = next(self.tokens)
        except StopIteration:
            self.current_token = None

    def parse(self) -> ParserNode:
        if self.current_token == None:
            return None

        result = self.expression()

        if self.current_token != None:
            self.throw()

        return result

    def expression(self) -> ParserNode:
        result = self.term()

        while self.current_token != None and self.current_token.type in [
            TokenType.UNION
        ]:
            if self.current_token.type == TokenType.UNION:
                self.forward()
                result = UnionNode(result, self.term())

        return result

    def term(self) -> ParserNode:
        result = self.symbol()

        while self.current_token != None and self.current_token.type in [
            TokenType.CONCATENATION
        ]:
            if self.current_token.type == TokenType.CONCATENATION:
                self.forward()
                result = ConcatNode(result, self.term())

        return result

    def symbol(self) -> ParserNode:
        token = self.current_token

        # Opens new expression with parenthesis
        if token.type == TokenType.LEFT_PARENTHESIS:
            self.forward()

            expr = self.expression()

            if (
                self.current_token == None
                or self.current_token.type != TokenType.RIGHT_PARENTHESIS
            ):
                raise Exception("Expected ')'")

            self.forward()
            return self.unary_lookahead(expr)

        if token.type == TokenType.SYMBOL:
            self.forward()
            return self.unary_lookahead(SymbolNode(token.value))

        raise Exception("Unexpected token")

    def unary_lookahead(self, context) -> ParserNode:
        if (
            self.current_token is not None
            and self.current_token.type == TokenType.KLEENE_CLOSURE
        ):
            self.forward()
            return KleeneClosureNode(context)
        elif (
            self.current_token is not None
            and self.current_token.type == TokenType.POSITIVE_CLOSURE
        ):
            self.forward()
            return PositiveClosureNode(context)
        else:
            return context
