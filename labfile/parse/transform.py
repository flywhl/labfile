from decimal import Decimal
from lark import Transformer, Token
import logging
from typing import Any, Type, TypeAlias, TypeVar, Union
from pydantic import BaseModel
from abc import ABC, abstractmethod

from labfile.model.labfile import (
    Process,
    Labfile,
    Model,
    Provider,
    Resource,
    ValueReference,
)
from typing import Optional

logger = logging.getLogger(__name__)


### INTERMEDIATE REPRESENTATION #################

LiteralValue: TypeAlias = Union[int, float, str]


class Defn(BaseModel, ABC):
    @abstractmethod
    def to_domain(self, symbols: "SymbolTable") -> Model: ...


D = TypeVar("D", bound=Defn)


class SymbolTable(BaseModel):
    table: dict[str, Defn]

    def lookup(self, key: str, expecting: Type[D] = Defn) -> Optional[D]:
        val = self.table.get(key)
        if not val:
            return None

        if not isinstance(val, expecting):
            raise TypeError(
                f"Expected {expecting} but found symbol of type {type(val)}"
            )

        return val


class Reference(BaseModel):
    """A reference to a resource"""

    resource: str
    attribute: str

    @property
    def path(self) -> str:
        return f"{self.resource}.{self.attribute}"

    def to_domain(self, symbols: SymbolTable) -> Model:
        owner = symbols.lookup(self.resource, expecting=ResourceDefinition)
        if not owner:
            raise ValueError(f"Could not find {self.path} in the symbol table.")
        return ValueReference(
            owner=owner.to_domain(symbols), attribute=self.attribute
        )  # TODO: fix typing


class Parameter(BaseModel):
    name: str
    value: LiteralValue | Reference


class ParameterSet(BaseModel):
    values: dict[str, LiteralValue | Reference]

    @classmethod
    def from_parameters(cls, parameters: list[Parameter]) -> "ParameterSet":
        return cls(values={param.name: param.value for param in parameters})


### RESOURCES ##########


class ResourceDefinition(Defn, ABC):
    name: str

    @abstractmethod
    def to_domain(self, symbols: "SymbolTable") -> Resource: ...


class ProcessDefinition(ResourceDefinition):
    parameters: ParameterSet
    via: str

    def to_domain(self, symbols: SymbolTable) -> Process:
        parameters = {
            name: self._build_parameter(value, symbols)
            if isinstance(value, Reference)
            else value
            for name, value in self.parameters.values.items()
        }

        process = Process(
            name=self.name,
            parameters=parameters,
            via=self.via,
        )

        return process

    def _build_parameter(self, value: Reference, symbols: SymbolTable):
        ref_name = value.path.split(".")[0]

        # the thing being pointed to
        ref_symbol = symbols.lookup(ref_name, expecting=ResourceDefinition)
        if not ref_symbol:
            raise ValueError(f"Referenced process {ref_name} not found")

        return ValueReference(owner=ref_symbol.to_domain(symbols), attribute=value.path)


class ProviderDefinition(ResourceDefinition):
    def to_domain(self, symbols: SymbolTable) -> Provider:
        return Provider(name=self.name)


### TRANSFORMER #################################


class LabfileTransformer(Transformer):
    """Convert an AST into a Domain object"""

    def start(self, items: list[ResourceDefinition]) -> Labfile:
        symbol_table: SymbolTable = SymbolTable(
            table={item.name: item for item in items}
        )

        resources = [item.to_domain(symbol_table) for item in items]

        processes = [
            resource for resource in resources if isinstance(resource, Process)
        ]
        providers = [
            resource for resource in resources if isinstance(resource, Provider)
        ]

        return Labfile(processes=processes, providers=providers)

    def statement(self, items: list[Any]) -> Any:
        return items[0]

    def provider(self, items: list[Union[Token, ParameterSet]]) -> ProviderDefinition:
        provider_name = str(items[0])
        return ProviderDefinition(name=provider_name)

    def experiment(
        self, items: list[Union[Token, str, ParameterSet]]
    ) -> ProcessDefinition:
        # experiment_name = str(items[0])
        experiment_alias = str(items[1])
        via = items[2]
        with_parameters = items[3]
        if not isinstance(with_parameters, ParameterSet):
            raise ValueError("Expected ParameterSet for experiment parameters")
        if not isinstance(via, str):
            raise ValueError("Expected string for experiment path")

        return ProcessDefinition(
            name=experiment_alias, parameters=with_parameters, via=via
        )

    def via_clause(self, items: list[str]) -> str:
        return items[0]

    def with_clause(self, items: list[Parameter]) -> ParameterSet:
        return ParameterSet.from_parameters(items)

    def with_param(self, items: list[Token]) -> Parameter:
        value_token = items[1]
        value = (
            value_token
            if isinstance(value_token, Reference)
            else self._convert_value(value_token)
        )
        return Parameter(name=str(items[0]), value=value)

    def value(self, items: list[Union[Token, Reference]]) -> Union[Token, Reference]:
        return items[0]

    def reference(self, items: list[Token]) -> Reference:
        resource = items[0]
        attribute = items[1]
        return Reference(resource=resource, attribute=attribute)

    def dotted_identifier(self, items: list[Token]) -> str:
        return ".".join(str(item) for item in items)

    def simple_identifier(self, items: list[Token]) -> str:
        return str(items[0])

    ### PRIVATE #################################

    def _convert_value(self, token: Token) -> LiteralValue:
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
