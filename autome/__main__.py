import json
from pathlib import Path
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
        case ['.automata', '.json']:
            lexer = Lexico.parse(input)
        case ['.lexer', '.json']:
            lexer = Lexico(input)
        case other:
            print(f"Invalid input format: {''.join(other)}")
            exit()

    lexer.run(source)
    
    if output is not None:
        lexer.save(output)
    
@cli.command()
@click.argument("input")
def sin(input: Path):
    # cfg = CFG.parse(input)
    cfg = CFG.parse(input)

if __name__ == '__main__':
    cli()
