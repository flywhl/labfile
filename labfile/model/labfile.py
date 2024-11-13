from typing import TypeAlias, Union
from pydantic import BaseModel, Field

ParameterValue: TypeAlias = Union[int, float, str]
Parameters: TypeAlias = dict[str, ParameterValue | "ValueReference"]


class Model(BaseModel):
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({super().__str__()})"


class Resource(Model):
    """A top-level entity in a Labfile"""


class ValueReference(Model):
    """A reference to a value in another resource"""

    owner: Resource
    attribute: str


class Process(Resource):
    """A resource which ingests parameters and outputs a result"""

    name: str
    parameters: dict[str, ParameterValue | ValueReference]
    via: str


class Provider(Resource):
    """A resource which adapts a Process to an executable piece of software"""

    name: str


class Dataset(Resource):
    """A resource which exposes data to a process"""


class Labfile(Model):
    """The Labfile."""

    providers: list[Provider]
    processes: list[Process]
    datasets: list[Dataset] = Field(default_factory=list)
