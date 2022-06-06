from autome.regex.lexer import Lexer
from autome.regex.nodes import ConcatNode, KleeneClosureNode, SymbolNode, UnionNode
from autome.regex.parser import Parser


def test_regex_parser():
    lexer = Lexer("(a|b) b*")

    tokens = lexer.generate_tokens()

    parser = Parser(tokens)

    expected = ConcatNode(
        UnionNode(
            SymbolNode("a"),
            SymbolNode("b"),
        ),
        KleeneClosureNode(SymbolNode("b")),
    )

    tree = parser.parse()

    assert tree == expected
