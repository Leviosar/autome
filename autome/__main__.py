import json
from pathlib import Path
from pprint import pprint
import click
from autome.finite_automata.parsers import JSONConverter
from autome.grammars.cfg import CFG
from autome.interface import Lexico


@click.group()
def cli():
    pass


@cli.command()
@click.argument("input", type=click.Path(exists=True, path_type=Path))
@click.argument("source", type=click.Path(exists=True, path_type=Path))
@click.option("--output", type=click.Path(path_type=Path))
def lexico(input: Path, source: Path, output: Path):
    match input.suffixes:
        case [".automata", ".json"]:
            lexer = Lexico.parse(input)
        case [".lexer", ".json"]:
            lexer = Lexico(input)
        case other:
            print(f"Invalid input format: {''.join(other)}")
            exit()

    tokens = lexer.run(source)

    grammar = CFG.parse(input)

    validated = grammar.accept(" ".join([token.type for token in tokens]), True)

    print(validated)

    if output is not None:
        lexer.save(output)


@cli.command()
@click.argument("input")
def sin(input: Path):
    cfg = CFG.parse(input)
    print(cfg)
    cfg.calculate_first()
    cfg.calculate_follow()
    cfg.eliminate_left_recursion()
    cfg.left_factoring()
    print(cfg.accept("binary operator binary".strip(), True))


if __name__ == "__main__":
    cli()
