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


### TRANSFORMER #################################


class LabfileTransformer(Transformer):
    """Convert an AST into a Domain object"""

    def start(self, items: list[ASTNode]) -> LabfileNode:
        processes = [
            item for item in items if isinstance(item, ProcessNode)
        ]
        providers = [
            item for item in items if isinstance(item, ProviderNode)
        ]
        
        return LabfileNode(processes=processes, providers=providers)

    def statement(self, items: list[Any]) -> Any:
        return items[0]

    def provider(self, items: list[Union[Token, dict]]) -> ProviderNode:
        provider_name = str(items[0])
        return ProviderNode(name=provider_name)

    def experiment(
        self, items: list[Union[Token, str, dict]]
    ) -> ProcessNode:
        experiment_alias = str(items[1])
        via = items[2]
        parameters = items[3]
        
        if not isinstance(via, str):
            raise ValueError("Expected string for experiment path")

        return ProcessNode(
            name=experiment_alias,
            parameters=parameters,
            via=via
        )

    def via_clause(self, items: list[str]) -> str:
        return items[0]

    def with_clause(self, items: list[ParameterNode]) -> dict:
        return {param.name: param.value for param in items}

    def with_param(self, items: list[Token]) -> ParameterNode:
        value_token = items[1]
        value = (
            value_token
            if isinstance(value_token, ReferenceNode)
            else self._convert_value(value_token)
        )
        return ParameterNode(name=str(items[0]), value=value)

    def value(self, items: list[Union[Token, ReferenceNode]]) -> Union[Token, ReferenceNode]:
        return items[0]

    def reference(self, items: list[Token]) -> ReferenceNode:
        resource = str(items[0])
        attribute = str(items[1])
        return ReferenceNode(resource_name=resource, attribute_path=attribute)

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
