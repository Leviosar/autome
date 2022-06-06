import itertools
from autome.regex.lexer import Lexer, Token, TokenType


def test_regex_lexer():
    lexer = Lexer("(a|b)* (c|d)*")

    tokens = lexer.generate_tokens()

    expected = iter(
        [
            Token(TokenType.LEFT_PARENTHESIS),
            Token(TokenType.SYMBOL, "a"),
            Token(TokenType.UNION),
            Token(TokenType.SYMBOL, "b"),
            Token(TokenType.RIGHT_PARENTHESIS),
            Token(TokenType.KLEENE_CLOSURE),
            Token(TokenType.CONCATENATION),
            Token(TokenType.LEFT_PARENTHESIS),
            Token(TokenType.SYMBOL, "c"),
            Token(TokenType.UNION),
            Token(TokenType.SYMBOL, "d"),
            Token(TokenType.RIGHT_PARENTHESIS),
            Token(TokenType.KLEENE_CLOSURE),
        ]
    )

    assert all(a == b for a, b in itertools.zip_longest(tokens, expected))
