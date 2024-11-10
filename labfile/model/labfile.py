from typing import TypeAlias, Union
from pydantic import BaseModel

ParameterValue: TypeAlias = Union[int, float, str]
Parameters: TypeAlias = dict[str, ParameterValue | "ValueReference"]


class Model(BaseModel):
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({super().__str__()})"


class Resource(Model): ...


class ValueReference(Model):
    owner: Resource
    attribute: str


class Experiment(Resource):
    name: str
    parameters: dict[str, ParameterValue | ValueReference]
    via: str


class Provider(Resource):
    name: str


class Labfile(Model):
    providers: list[Provider]
    experiments: list[Experiment]
