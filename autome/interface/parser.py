from typing import List
import click
from tabulate import tabulate

from autome.grammars.cfg import CFG
from autome.utils.dataclasses import Token


def display_analysis_table(grammar, table):
    return
    print("TABLE")
    headers = ["..."] + grammar.terminals
    data = []

    for row in table:
        data_row = [row]
        for item in table[row]:
            pass
            print(item)

        data.append(data_row)

    print(tabulate(data, headers=headers))

class Parser:
    def __init__(self, grammar: CFG) -> None:
        self.grammar = grammar

    @classmethod
    def parse(cls, input: click.Path):
        grammar = CFG.parse(input)
        return Parser(grammar)

    def validate(self, tokens: List[Token]):
        return self.grammar.accept(tokens)