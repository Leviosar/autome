from autome.regular_expression import Lexer, Parser, Interpreter
from autome.regular_expression.nodes import ConcatNode, KleeneClosureNode, SymbolNode, UnionNode
from itertools import tee


def test_regex_interpreter():
    lexer = Lexer("(a|b)* (c|d)*")

    tokens = lexer.generate_tokens()
    
    parser = Parser(tokens)
    
    tree = parser.parse()

    interpreter = Interpreter()

    machine = interpreter.run(tree)
    print('break')
    print(machine)
    print(machine.determinize())
    assert machine.accepts("")
    assert machine.accepts("aaacdcdcd")
    assert machine.accepts("abcd")
    assert machine.accepts("badc")
    assert machine.accepts("bbbaaaddddccc")
    assert machine.accepts("a")
    assert machine.accepts("b")
    assert machine.accepts("c")
    assert machine.accepts("d")
    assert not machine.accepts("acbd")
    assert not machine.accepts("ddddbbbccccaaaa")