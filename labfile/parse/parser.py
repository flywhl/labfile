from pathlib import Path

from lark import Lark, Tree

from labfile.model.tree import LabfileNode
from labfile.parse.transform import LabfileTransformer
from labfile.config import Config


def _build_parser(grammar: Path) -> Lark:
    assert grammar.exists(), f"Grammar not found: {grammar}"
    labfile_grammar = grammar.read_text()

    return Lark(labfile_grammar, start="start", parser="lalr")


class Parser:
    def __init__(
        self,
        transformer: LabfileTransformer = LabfileTransformer(),
        config: Config = Config(),
    ) -> None:
        self._parser = _build_parser(config.grammar_path)
        self._transformer = transformer

    def parse(self, source: str) -> LabfileNode:
        ast = self._parse_to_ast(source)
        return self._parse_to_domain(ast)

    ### PRIVATE #################################

    def _parse_to_ast(self, source: str) -> Tree:
        return self._parser.parse(source)

    def _parse_to_domain(self, ast: Tree) -> LabfileNode:
        return self._transformer.transform(ast)


def parse(labfile: Path) -> LabfileNode:
    parser = Parser()
    return parser.parse(labfile.read_text())
