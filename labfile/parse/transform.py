from decimal import Decimal
from lark import Transformer, Token
import logging
from typing import Any, TypeAlias, Union
from pydantic import BaseModel
from abc import ABC, abstractmethod

from labfile.model.labfile import Experiment, Labfile, Provider

logger = logging.getLogger(__name__)

### INTERMEDIATE REPRESENTATION #################

ParameterValue: TypeAlias = Union[int, float, str]


class ExperimentName(BaseModel):
    value: str

    @classmethod
    def from_token(cls, token: Token) -> "ExperimentName":
        return cls(value=str(token))


class Parameter(BaseModel):
    name: str
    value: ParameterValue

    @classmethod
    def create_hyperparameter(cls, name: str, value: ParameterValue) -> "Parameter":
        return cls(name=name, value=value)


class ParameterSet(BaseModel):
    values: dict[str, ParameterValue]

    @classmethod
    def from_parameters(cls, parameters: list[Parameter]) -> "ParameterSet":
        return cls(values={param.name: param.value for param in parameters})


class ResourceDefinition(BaseModel, ABC):
    name: str

    @abstractmethod
    def to_domain(self) -> BaseModel: ...


class ExperimentDefinition(ResourceDefinition):
    parameters: ParameterSet
    path: str

    def to_domain(self) -> Experiment:
        return Experiment(
            name=self.name,
            parameters=self.parameters.values,
            path=self.path
        )


class ProviderDefinition(ResourceDefinition):
    def to_domain(self) -> Provider:
        return Provider(name=self.name)


### TRANSFORMER #################################


class LabfileTransformer(Transformer):
    """Convert an AST into a Domain object"""

    def start(self, items: list[ResourceDefinition]) -> Labfile:
        resources = [item.to_domain() for item in items]
        experiments = [
            resource for resource in resources if isinstance(resource, Experiment)
        ]

        providers = [
            resource for resource in resources if isinstance(resource, Provider)
        ]
        return Labfile(experiments=experiments, providers=providers)

    def statement(self, items: list[Any]) -> Any:
        return items[0]

    def provider(self, items: list[Union[Token, ParameterSet]]) -> ProviderDefinition:
        provider_name = str(items[0])
        return ProviderDefinition(name=provider_name)

    def experiment(
        self, items: list[Union[Token, str, ParameterSet]]
    ) -> ExperimentDefinition:
        experiment_name = str(items[1])
        experiment_alias = str(items[2])
        path = items[3]
        parameters = items[4]
        if not isinstance(parameters, ParameterSet):
            raise ValueError("Expected ParameterSet for experiment parameters")
        if not isinstance(path, str):
            raise ValueError("Expected string for experiment path")

        return ExperimentDefinition(
            name=experiment_alias,
            parameters=parameters,
            path=path
        )

    def via_clause(self, items: list[str]) -> str:
        return items[0]

    def with_clause(self, items: list[Parameter]) -> ParameterSet:
        return ParameterSet.from_parameters(items)

    def with_param(self, items: list[Token]) -> Parameter:
        return Parameter.create_hyperparameter(
            name=str(items[0]), value=self._convert_value(items[1])
        )

    def value(self, items: list[Token]) -> Token:
        return items[0]

    def dotted_identifier(self, items: list[Token]) -> str:
        return ".".join(str(item) for item in items)

    def simple_identifier(self, items: list[Token]) -> str:
        return str(items[0])

    ### PRIVATE #################################

    def _convert_value(self, token: Token) -> ParameterValue:
        """Convert string values to appropriate numeric types"""
        value = str(token)
        is_numeric = value.replace(".", "", 1).isdigit()
        if is_numeric:
            if "." in value:
                # Use Decimal for exact decimal representation
                return float(Decimal(value))
            return int(value)
        else:
            return value
