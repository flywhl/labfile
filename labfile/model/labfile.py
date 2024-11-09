from typing import TypeAlias, Union
from pydantic import BaseModel

ParameterValue: TypeAlias = Union[int, float, str]


class Experiment(BaseModel):
    name: str
    parameters: dict[str, ParameterValue]
    path: str


class Provider(BaseModel):
    name: str


class Labfile(BaseModel):
    providers: list[Provider]
    experiments: list[Experiment]
