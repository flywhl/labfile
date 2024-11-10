from pathlib import Path
from pprint import pprint
from labfile.model.labfile import Labfile
from labfile import parse


def test_parse_should_work():
    labfile_path = Path(__file__).parent / "Labfile.test"
    labfile = parse(labfile_path)
    assert isinstance(labfile, Labfile)
    pprint(labfile)
