from autome.regex.lexer import Lexer
from autome.regex.nodes import ConcatNode, KleeneClosureNode, SymbolNode, UnionNode
from autome.regex.parser import Parser


def test_regex_parser():
    """Test case for transforming a regular expression into a execution tree using the parser"""
    lexer = Lexer("(a|b)* (c|d)*")

    tokens = lexer.generate_tokens()

    parser = Parser(tokens)

    expected = ConcatNode(
        KleeneClosureNode(
            UnionNode(
                SymbolNode("a"),
                SymbolNode("b"),
            ),
        ),
        KleeneClosureNode(
            UnionNode(
                SymbolNode("c"),
                SymbolNode("d"),
            ),
        ),
    )

    tree = parser.parse()

    assert tree == expected
