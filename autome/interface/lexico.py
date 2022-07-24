from ast import keyword, parse
from dataclasses import dataclass
from email import header
import json
from operator import le
import pathlib
from typing import Dict, List, Optional, Union
import click
from autome.finite_automata.machine import DeterministicFiniteAutomata
from autome.finite_automata.parsers import JSONConverter
from autome.finite_automata.state import State
from autome.regex import Regex, lexer
from autome.regex.blocks import UnionAutomata
from tabulate import tabulate


@dataclass
class Definition:
    name: str
    expression: str
    regex: Optional[Regex] = None

    def __repr__(self):
        return f"{self.name} => {self.expression}"

    def dict(self):
        return {"name": self.name, "expression": self.expression}


@dataclass
class Token:
    type: str
    value: str

    def __repr__(self) -> str:
        return f"{self.type}:{self.value}"


class Lexico:
    """
    Interface for generating lexical analyzers using Thompson's building algorithm
    """

    keywords: List[str]
    """
    List of keywords for the language, keywords will be used as a special type of token,
    evaluated before the other types and with higher precedence
    """
    definitions: List[Definition]
    """
    List of regular definitions used to compose more complex tokens
    A regular definition itself WILL NOT be evaluated as a token type
    """
    tokens: List[Definition]
    """
    List of token definitions that will be used by the lexer as rules for findind tokens 
    in a source code. Tokens are created in order, so you can use already defined tokens
    as part of the definition of the later tokens, e.g:
        
    digit => 0|1|2|3|4|5|6|7|8|9

    float => digit* . digit* 
    """
    lexer: DeterministicFiniteAutomata
    """
    The machine actually evaluating the code.
    """

    def __init__(self, input: Union[click.Path, pathlib.Path, None]) -> None:
        if input is None:
            pass
        elif isinstance(input, click.Path) or isinstance(input, pathlib.Path):
            self.input = self.parse_input(input)
            self.lexer = self.build_lexer()
        else:
            print(type(input))
            raise Exception("Invalid arguments")

    @classmethod
    def parse(cls, input: Union[click.Path, pathlib.Path]):
        """Parses the input file with the definitions of a lexical analyzer into useful data for the program"""
        with open(input) as file:
            content = json.load(file)

        instance = Lexico(None)
        instance.keywords = content["reserved-keywords"]
        instance.definitions = [
            Definition(definition["name"], definition["expression"])
            for definition in content["definitions"]
        ]
        instance.tokens = [
            Definition(definition["name"], definition["expression"])
            for definition in content["tokens"]
        ]
        instance.lexer = JSONConverter.parse(content["automata"])

        return instance

    def parse_input(self, input: click.Path):
        """Parses the input file with the definitions of a lexical analyzer into useful data for the program"""
        with open(input) as file:
            content = json.load(file)

        self.keywords = content["reserved-keywords"]
        self.definitions = [
            Definition(definition["name"], definition["expression"])
            for definition in content["definitions"]
        ]
        self.tokens = [
            Definition(definition["name"], definition["expression"])
            for definition in content["tokens"]
        ]

    def save(self, output: click.Path) -> None:
        converter = JSONConverter()

        model = converter.serialize(self.lexer)

        data = {
            "reserved-keywords": self.keywords,
            "definitions": [definition.dict() for definition in self.definitions],
            "tokens": [token.dict() for token in self.tokens],
            "automata": model,
        }

        with open(output, "w+") as fp:
            fp.write(json.dumps(data))

    def build_lexer(self) -> DeterministicFiniteAutomata:
        """
        Uses the regular definitions and token definitions to build a DFA that can identify tokens of
        the defined language. It's a huge DFA which accepts any word of any of the definitions passed
        as arguments, identifiying the type of token by a label 'type' marked on the final states of
        the 'building' automatas
        """
        data = self.definitions + self.tokens
        data = [[entry.name, entry.expression] for entry in data]

        headers = ["Nome", "Expressão"]
        print(tabulate(data, headers=headers, tablefmt="fancy_grid"))

        defined_tokens: List[Definition] = []
        for token in self.tokens:
            for definition in self.definitions:
                if definition.name in token.expression:
                    token.expression = token.expression.replace(
                        definition.name, f"({definition.expression})"
                    )

            for defined_token in defined_tokens:
                if defined_token.name in token.expression:
                    token.expression = token.expression.replace(
                        defined_token.name, f"({defined_token.expression})"
                    )

            token.regex = Regex(token.expression)
            defined_tokens.append(token)

        for i in range(len(self.tokens)):
            if i == 0:
                first = self.tokens[i].regex.automata()
                for state in first.final():
                    state.type = self.tokens[i].name

                machine = first
            else:
                next = self.tokens[i].regex.automata()
                for state in next.final():
                    state.type = self.tokens[i].name
                machine = UnionAutomata(machine, next)

        print("Espera um pouquinho que eu sou meio devagar...")
        return machine.determinize().clone().minimize()

    def run(self, code: click.Path) -> List[Dict[str, str]]:
        """
        Evaluates a given source code with a previously built lexer.

        If at any time there's a symbol the DFA can't recognize, or a invalid token pattern, raises an
        exception. Otherwise, returns a list of the recognized tokens.
        """
        self.lexer.create_transition_map()
        print(self.lexer)

        with open(code) as source_file:
            source = source_file.read()

        source = source.strip()

        data = []
        lines = source.split("\n")
        for index, line in enumerate(lines):
            data.append([index, line])
        print(tabulate(data, headers=["Source code"], tablefmt="fancy_grid"))

        found: List[Token] = []

        i = 0
        while i < len(source):
            word = ""

            while i < len(source) and source[i] != " " and source[i] != "\n":
                word += source[i]
                i += 1

            if word in self.keywords:
                found.append(Token("keyword", word))
                i += 1
                continue

            if self.lexer.accepts(word):
                type = self.lexer.step_stack[-1].destiny.type

                found.append(Token(type, word))
            else:
                if word != "":
                    raise Exception(f"Lexical Error {word}")

            i += 1

        data = []
        for entry in found:
            data.append([entry.type, entry.value])
        print(tabulate(data, headers=["TokenType", "Value"], tablefmt="fancy_grid"))

        print(found)
        return found
