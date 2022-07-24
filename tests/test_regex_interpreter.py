from autome.regex import Lexer, Parser, Interpreter
from autome.regex.nodes import ConcatNode, KleeneClosureNode, SymbolNode, UnionNode
from itertools import tee


def test_regex_interpreter():
    lexer = Lexer("(a|b)* (c|d)*")

    tokens = lexer.generate_tokens()

    parser = Parser(tokens)

    tree = parser.parse()

    interpreter = Interpreter()

    machine = interpreter.run(tree).determinize()

    print(machine)

    assert machine.accepts("")
    assert machine.accepts("aaaabbbb")
    assert machine.accepts("abbababa")
    assert machine.accepts("ab")
    assert machine.accepts("a")
    assert machine.accepts("b")
    assert machine.accepts("abcd")
    assert machine.accepts("ccccc")
    assert machine.accepts("ddddd")
    assert machine.accepts("cccccddddd")
    assert not machine.accepts("acbd")
    assert not machine.accepts("ddddbbbccccaaaa")
