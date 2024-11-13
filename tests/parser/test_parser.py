from pathlib import Path
from pprint import pprint
from labfile import parse
from labfile.model.tree import LabfileNode


def test_parse_should_work():
    labfile_path = Path(__file__).parent / "Labfile.test"
    labfile = parse(labfile_path)
    assert isinstance(labfile, LabfileNode)
    pprint(labfile)
