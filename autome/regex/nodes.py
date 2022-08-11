from dataclasses import dataclass

from autome.regex.blocks import (
    SymbolAutomata,
    ConcatenationAutomata,
    UnionAutomata,
    KleeneAutomata,
    EpsilonAutomata,
)

from autome.automatas import NDFA


@dataclass
class ParserNode:
    def apply(self) -> "NDFA":
        raise NotImplementedError()


@dataclass
class SymbolNode(ParserNode):
    value: str

    def apply(self):
        # print(f'Entrou no symbol {self.value}')
        return SymbolAutomata(self.value) if self.value != "&" else EpsilonAutomata()

    def __repr__(self) -> str:
        return f"{self.value}"


@dataclass
class ConcatNode(ParserNode):
    node_a: any
    node_b: any

    def apply(self):
        # print(f'Entrou no concat {self.node_a} . {self.node_b}')
        return ConcatenationAutomata(self.node_a.apply(), self.node_b.apply())

    def __repr__(self) -> str:
        return f"({self.node_a} . {self.node_b})"


@dataclass
class UnionNode(ParserNode):
    node_a: any
    node_b: any

    def apply(self):
        # print(f'Entrou no union {self.node_a} | {self.node_b}')
        return UnionAutomata(self.node_a.apply(), self.node_b.apply())

    def __repr__(self) -> str:
        return f"({self.node_a} | {self.node_b})"


@dataclass
class KleeneClosureNode(ParserNode):
    node: any

    def apply(self):
        # print(f'Entrou no kleene {self.node}')
        return KleeneAutomata(self.node.apply())

    def __repr__(self) -> str:
        return f"({self.node})*"


@dataclass
class PositiveClosureNode(ParserNode):
    node: any

    def apply(self):
        return PositiveClosureNode(self.node.apply())

    def __repr__(self) -> str:
        return f"({self.node})+"
