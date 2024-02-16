import re
import types
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Optional

import yaml

from engine.exceptions import BadAddress, BadNode

# Base Nodes ------------------------------------------------------------------


class Node:
    data: Any

    def get_addr(self, address: list[str | int]):
        current_node = self

        for addr in address:
            current_node = current_node[addr]

        return current_node

    @property
    def type(self):
        return self.__class__.__name__


NodeType = type[Node]
NodeTypes = tuple[NodeType]


@dataclass
class Expression(Node):
    data: str
    pattern: str = ".*"

    def __getitem__(self, index: Any = None):
        if index is not None:
            raise BadAddress("Terminal {self.type} accessed with index {index}")


ExpressionType = type[Expression]
ExpressionTypes = tuple[ExpressionType]


@dataclass
class Sequence(Node):
    data: list

    def __getitem__(self, index: int):
        if not isinstance(index, int):
            raise BadAddress(f"Sequence node requires integer index. Given: {index}.")
        if index < 0:
            raise BadAddress(f"Negative index {index} is not allowed.")
        if index + 1 > len(self.data):
            raise BadAddress(f"No subnode at index {index} in node {self}.")
        return self.data[index]


SequenceType = type[Sequence]
SequenceTypes = tuple[SequenceType]


@dataclass
class Tag:
    key: str
    type: Node
    optional: bool = False


class Spec:
    tags: list[Tag]

    def __init__(self, *tags):
        self.tags = tags
        self.compile()

    def compile(self):
        self.keys = [tag.key for tag in self.tags]
        self.required_keys = [tag.key for tag in self.tags if not tag.optional]
        self.optional_keys = [tag.key for tag in self.tags if not tag.optional]

    def __iter__(self):
        return iter(self.tags)


@dataclass
class Map(Node):
    data: dict
    spec: Spec

    def __getitem__(self, key: str):
        if not isinstance(key, str):
            raise BadAddress(f"Map node requires string index. Given: {key}.")

        if key not in self.spec.keys:
            raise BadAddress(f"{self.type} node has no {key} key.")

        if key not in self.data:
            if key in self.spec.optional_keys:
                return None
            raise BadNode("{self.type} Map node missing a required key: {key}")

        return self.data[key]


MapType = type[Map]
MapTypes = tuple[MapType]


# Syntax ----------------------------------------------------------------------


@dataclass
class Syntax:
    types: NodeTypes

    @property
    def expressions(self) -> ExpressionTypes:
        return self.by_type(Expression)

    @property
    def sequences(self) -> SequenceTypes:
        return self.by_type(Sequence)

    @property
    def maps(self) -> MapTypes:
        return self.by_type(Map)

    def by_type(self, target_type: NodeType) -> NodeTypes:
        return [t for t in self.types if issubclass(t, target_type)]

    def extend(self, *new_types: NodeTypes) -> "Syntax":
        return replace(self, types=self.types + list(new_types))


# Initial syntax --------------------------------------------------------------


empty_syntax = Syntax(types=[])

initial_syntax = Syntax(types=[Expression, Sequence])


# Basic Syntax ----------------------------------------------------------------


@dataclass
class Null(Node):
    data: None = None


@dataclass
class A(Map):
    spec: Spec = Spec(
        Tag("a", Expression),
    )


@dataclass
class If(Map):
    spec: Spec = Spec(
        Tag("if", Expression),
        Tag("then", Sequence),
        Tag("else", Sequence, optional=True),
    )


@dataclass
class Doc(Map):
    spec: Spec = Spec(
        Tag("blocks", Sequence),
    )


@dataclass
class Blocks(Sequence):
    pass


@dataclass
class Block(Map):
    spec: Spec = Spec(
        Tag("name", Expression),
        Tag("content", Sequence),
    )


@dataclass
class Content(Sequence):
    pass


@dataclass
class Goto(Map):
    spec: Spec = Spec(
        Tag("goto", Expression),
    )


@dataclass
class GoSub(Map):
    spec: Spec = Spec(
        Tag("gosub", Expression),
    )


@dataclass
class Choice(Map):
    spec: Spec = Spec(
        Tag("choice", Expression),
        Tag("effects", Content),
        Tag("text", Expression, optional=True),
        # Tags ommited:
        # Tag("shown_effects", Sequence[ShownEffect], optional=True),
        # Tag("reusable", Expression, optional=True),
    )


@dataclass
class Print(Map):
    spec: Spec = Spec(
        Tag("print", Expression),
    )


@dataclass
class Error(Map):
    spec: Spec = Spec(
        Tag("error", Null),
    )


@dataclass
class Return(Map):
    spec: Spec = Spec(
        Tag("return", Null),
    )


@dataclass
class Wait(Map):
    spec: Tags = (Tag("wait", Null),)


@dataclass
class Variable(Expression):
    pattern: str = "^[a-zA-Z_][a-zA-Z0-9_]*$"


@dataclass
class Text(Expression):
    pattern: str = "[a-zA-Z_]*"


simple_syntax = initial_syntax.extend(
    If,
    A,
    Variable,
    Doc,
    Block,
    Goto,
    GoSub,
    Choice,
    Print,
    Error,
    Text,
    Null,
    Return,
    Wait,
)
syntax_v1 = simple_syntax


node_class_dict = {"A": A, "print": Print, "wait": Wait}
