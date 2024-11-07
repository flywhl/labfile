from pathlib import Path
from labfile.parse.parser import Labfile


def test_foo():
    labfile = Path(__file__).parent / "Labfile.test"
    parser = Labfile()
    project = parser.parse(labfile.read_text())
    print(project)
