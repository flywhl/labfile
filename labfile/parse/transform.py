from decimal import Decimal
from lark import Transformer, Token
import logging
from typing import Any, TypeAlias, Union
from pydantic import BaseModel
from abc import ABC, abstractmethod

from labfile.model.labfile import (
    Experiment,
    Labfile,
    Provider,
    Reference as ModelReference,
)
from typing import Optional

logger = logging.getLogger(__name__)

### INTERMEDIATE REPRESENTATION #################


class Reference(BaseModel):
    owner: Optional[Experiment] = None
    path: str

    def to_domain(self, owner: Experiment) -> ModelReference:
        return ModelReference(owner=owner, path=self.path)


ParameterValue: TypeAlias = Union[int, float, str, Reference]


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

    def to_domain(self, exp_lookup: dict[str, "ExperimentDefinition"]) -> Experiment:
        exp = Experiment(
            name=self.name,
            parameters={},  # Start with empty parameters
            path=self.path,
        )
        
        # Then populate parameters, converting references
        for name, value in self.parameters.values.items():
            if isinstance(value, Reference):
                # Get the referenced experiment name from the path
                ref_exp_name = value.path.split('.')[0]
                if ref_exp_name not in exp_lookup:
                    raise ValueError(f"Referenced experiment {ref_exp_name} not found")
                    
                # Convert the referenced experiment definition to domain model
                referenced_exp = exp_lookup[ref_exp_name].to_domain(exp_lookup)
                exp.parameters[name] = value.to_domain(owner=referenced_exp)
            else:
                exp.parameters[name] = value
                
        return exp


class ProviderDefinition(ResourceDefinition):
    def to_domain(self) -> Provider:
        return Provider(name=self.name)


### TRANSFORMER #################################


class LabfileTransformer(Transformer):
    """Convert an AST into a Domain object"""

    def start(self, items: list[ResourceDefinition]) -> Labfile:
        # Create lookup of experiment definitions
        exp_defs = [item for item in items if isinstance(item, ExperimentDefinition)]
        exp_lookup = {exp.name: exp for exp in exp_defs}
        
        # Convert to domain objects with access to lookup
        resources = []
        for item in items:
            if isinstance(item, ExperimentDefinition):
                resources.append(item.to_domain(exp_lookup))
            else:
                resources.append(item.to_domain())
                
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
        experiment_name = str(items[0])
        experiment_alias = str(items[1])
        path = items[2]
        parameters = items[3]
        if not isinstance(parameters, ParameterSet):
            raise ValueError("Expected ParameterSet for experiment parameters")
        if not isinstance(path, str):
            raise ValueError("Expected string for experiment path")

        return ExperimentDefinition(
            name=experiment_alias, parameters=parameters, path=path
        )

    def via_clause(self, items: list[str]) -> str:
        return items[0]

    def with_clause(self, items: list[Parameter]) -> ParameterSet:
        return ParameterSet.from_parameters(items)

    def with_param(self, items: list[Token]) -> Parameter:
        return Parameter.create_hyperparameter(
            name=str(items[0]), value=self._convert_value(items[1])
        )

    def value(self, items: list[Union[Token, Reference]]) -> Union[Token, Reference]:
        return items[0]

    def reference(self, items: list[Token]) -> Reference:
        experiment_path = str(items[0])
        output_path = str(items[1])
        return Reference(path=f"{experiment_path}.{output_path}")

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
