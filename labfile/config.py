from pathlib import Path
from pydantic_settings import BaseSettings


SRC_ROOT = Path(__file__).parent


class Config(BaseSettings):
    _labfile_src_root: Path = SRC_ROOT

    grammar_filename: str = "labfile.lark"
    grammar_path: Path = _labfile_src_root / grammar_filename
