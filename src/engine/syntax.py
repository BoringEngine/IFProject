import re
import types
from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import yaml

from engine.exceptions import BadAddress, BadNode

# Base Nodes ------------------------------------------------------------------


class Nodes(Enum):
    BLOCK = "Block"
    BLOCKS = "Blocks"
    GOTO = "Goto"
    GOSUB = "GoSub"
    CHOICE = "Choice"
    PRINT = "Print"
    ERROR = "Error"
    RETURN = "Return"
    WAIT = "Wait"
    STUFF = "Content"


class Node:
    data: Any

    def get_addr(self, address: list[str | int]):
        current_node = self

        for index, addr in enumerate(address):
            try:
                current_node = current_node[addr]
            except Exception as e:
                raise BadAddress(
                    f"Error at address position {index}"
                    f" (value {addr}) in {address}: {e}"
                )

        return current_node

    @property
    def type(self):
        return self.__class__.__name__


NodeTuple = tuple[Nodes, ...]


@dataclass
class Value(Node):
    data: str
    pattern: str = ".*"

    def __getitem__(self, index: Any = None):
        if index is not None:
            raise BadAddress("Terminal {self.type} accessed with index {index}")

@dataclass
class Sequence(Node):
    data: list
    list_of: Nodes | Nodes = Node

    def __getitem__(self, index: int):
        if not isinstance(index, int):
            raise BadAddress(f"Sequence node requires integer index. Given: {index}.")
        if index < 0:
            raise BadAddress(f"Negative index {index} is not allowed.")
        if index + 1 > len(self.data):
            raise BadAddress(f"No subnode at index {index} in node {self}.")
        return self.data[index]

@dataclass
class Tag:
    key: str
    type: Nodes | str
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


# Syntax ----------------------------------------------------------------------


@dataclass
class Syntax:
    """A repository of node types. Provides methods to query and extend the syntax."""

    types: NodeTuple

    @property
    def expressions(self) -> NodeTuple:
        return self.by_type(Value)

    @property
    def sequences(self) -> NodeTuple:
        return self.by_type(Sequence)

    @property
    def maps(self) -> NodeTuple:
        return self.by_type(Map)

    def by_type(self, target_type: Nodes) -> NodeTuple:
        return tuple(t for t in self.types if issubclass(t, target_type))

    def extend(self, *new_types: Nodes) -> "Syntax":
        return replace(self, types=tuple([*self.types, *new_types]))

    def __getitem__(self, key: str) -> Nodes:
        for t in self.types:
            if t.__name__ == key:
                return t
        raise KeyError(f"Type {key} not found in syntax")


# Initial syntax --------------------------------------------------------------


empty_syntax = Syntax(types=())

initial_syntax = Syntax(types=(Value, Sequence))


# Basic Syntax ----------------------------------------------------------------


@dataclass
class Null(Node):
    data: None = None


@dataclass
class A(Map):
    spec: Tags = (Tag("a", Value),)


@dataclass
class If(Map):
    spec: Tags = (
        Tag("if", Value),
        Tag("then", Sequence),
        Tag("else", Sequence, optional=True),
    )


@dataclass
class Doc(Map):
    spec: Spec = Spec(
        Tag("blocks", Sequence),
    )


@dataclass
class Block(Map):
    spec: Spec = Spec(
        Tag("name", Expression),
        Tag("content", Sequence),
    )


@dataclass
class Blocks(Sequence):
    list_of: Nodes = Nodes.BLOCK


@dataclass
class Block(Map):
    spec: Tags = (
        Tag("name", Value),
        Tag("content", Nodes.STUFF, optional=True),
        Tag("blocks", Nodes.BLOCKS, optional=True),
    )


@dataclass
class Goto(Map):
    spec: Tags = (Tag("goto", Value),)


@dataclass
class GoSub(Map):
    spec: Tags = (Tag("gosub", Value),)


@dataclass
class Choice(Map):
    spec: Tags = (
        Tag("choice", Value),
        Tag("effects", Stuff),
        Tag("text", Value, optional=True),
        # Tags ommited:
        # Tag("shown_effects", Sequence[ShownEffect], optional=True),
        # Tag("reusable", Expression, optional=True),
    )


@dataclass
class Print(Map):
    spec: Tags = (Tag("print", Value),)


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
    spec: Spec = Spec(
        Tag("wait", Null),
    )


@dataclass
class Variable(Value):
    pattern: str = "^[a-zA-Z_][a-zA-Z0-9_]*$"


@dataclass
class Text(Value):
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
