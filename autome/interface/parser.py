from typing import List
import click

from autome.grammars.cfg import CFG
from autome.utils.dataclasses import Token

class Parser:
    def __init__(self, grammar: CFG) -> None:
        self.grammar = grammar

    @classmethod
    def parse(cls, input: click.Path):
        grammar = CFG.parse(input)
        return Parser(grammar)

    def validate(self, tokens: List[Token]):
        return self.grammar.accept(tokens, True)