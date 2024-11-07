from pathlib import Path

from lark import Lark, Tree

from labfile.model.project import Project
from labfile.parse.transform import LabfileTransformer


def _build_parser(grammar: Path) -> Lark:
    assert grammar.exists(), f"Grammar not found: {grammar}"
    labfile_grammar = grammar.read_text()

    return Lark(labfile_grammar, start="start", parser="lalr")


class Labfile:
    def __init__(self, grammar: Path, transformer: LabfileTransformer) -> None:
        self._parser = _build_parser(grammar)
        self._transformer = transformer

    def parse(self, source: str) -> Project:
        ast = self._parse_to_ast(source)
        return self._parse_to_domain(ast)

    ### PRIVATE #################################

    def _parse_to_ast(self, source: str) -> Tree:
        return self._parser.parse(source)

    def _parse_to_domain(self, ast: Tree) -> Project:
        return self._transformer.transform(ast)
