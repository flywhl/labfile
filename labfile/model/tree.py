from enum import Enum
from typing import TypeAlias, Union
from pydantic import BaseModel, Field

LiteralValue: TypeAlias = Union[int, float, str]


class ResourceKind(Enum):
    PROCESS = "process"
    PROVIDER = "provider"
    DATASET = "dataset"


class ASTNode(BaseModel):
    """Base class for all AST nodes"""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({super().__str__()})"


class ReferenceNode(ASTNode):
    """A reference to a value in another resource node"""

    resource_name: str
    attribute_path: str


class ParameterNode(ASTNode):
    """A parameter definition in the AST"""

    name: str
    value: Union[LiteralValue, ReferenceNode]


class ResourceNode(ASTNode):
    """Base node for any resource defined in the Labfile"""

    name: str
    kind: ResourceKind


class ProcessNode(ResourceNode):
    """AST node representing a process definition"""

    kind: ResourceKind = ResourceKind.PROCESS
    via: str
    parameters: dict[str, Union[LiteralValue, ReferenceNode]]


class ProviderNode(ResourceNode):
    """AST node representing a provider definition"""

    kind: ResourceKind = ResourceKind.PROVIDER


class DatasetNode(ResourceNode):
    """AST node representing a dataset definition"""

    kind: ResourceKind = ResourceKind.DATASET


class LabfileNode(ASTNode):
    """Root node of the Labfile AST"""

    providers: list[ProviderNode]
    processes: list[ProcessNode]
    datasets: list[DatasetNode] = Field(default_factory=list)
