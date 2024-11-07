from pathlib import Path
from labfile.config import Config
from labfile.parse.parser import Labfile
from labfile.parse.transform import LabfileTransformer


def test_foo():
    config = Config()
    labfile = Path(__file__).parent / "Labfile.test"
    transformer = LabfileTransformer()
    parser = Labfile(config.grammar_path, transformer)
    project = parser.parse(labfile.read_text())
    print(project)
