import types
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Optional

import yaml

from engine.exceptions import BadAddress, BadNode

# Base Nodes ------------------------------------------------------------------


class Node:
    data: Any

    def __getitem__(self, index: str | int):
        if (type(self.data) != list) and (type(self.data) != dict):
            raise BadAddress(f"Node {self} has data that is not a list or dict.")
        if (type(self.data) == list and type(index) != int) or (
            type(self.data) == dict and type(index) != str
        ):
            raise BadAddress(
                f"Incorrectly indexed into node {self} with key {index} of incorrect type."
            )
        try:
            return self.data[index]
        except (IndexError, KeyError):
            raise BadAddress(f"No subnode at index {index} in node {self}.")

    def get_addr(self, address: list[str | int], curr_addr_ind: Optional[int] = 0):
        if curr_addr_ind + 1 < len(address):
            return self[address[curr_addr_ind]].get_addr(address, curr_addr_ind + 1)
        elif curr_addr_ind + 1 == len(address):
            return self[address[curr_addr_ind]]
        elif curr_addr_ind == len(address):
            return self

        raise BadAddress(
            f"Address index {curr_addr_ind} is greter than the length of the address list {address}."
        )

    @property
    def type(self):
        return self.__class__.__name__


NodeType = type[Node]
NodeTypes = tuple[NodeType]


@dataclass
class Expression(Node):
    data: str
    pattern: str = ".*"


ExpressionType = type[Expression]
ExpressionTypes = tuple[ExpressionType]


@dataclass
class Sequence(Node):
    data: list


SequenceType = type[Sequence]
SequenceTypes = tuple[SequenceType]


@dataclass
class Tag:
    key: str
    type: Node
    optional: bool = False


Tags = list[Tag]


@dataclass
class Map(Node):
    data: dict
    spec: Tags


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
    spec: Tags = (Tag("a", Expression),)


@dataclass
class If(Map):
    spec: Tags = (
        Tag("if", Expression),
        Tag("then", Sequence),
        Tag("else", Sequence, optional=True),
    )


@dataclass
class Doc(Map):
    spec: Tags = (Tag("blocks", Sequence),)


@dataclass
class Blocks(Sequence):
    pass


@dataclass
class Block(Map):
    spec: Tags = (
        Tag("name", Expression),
        Tag("content", Sequence),
    )


@dataclass
class Content(Sequence):
    pass


@dataclass
class Goto(Map):
    spec: Tags = (Tag("goto", Expression),)


@dataclass
class GoSub(Map):
    spec: Tags = (Tag("gosub", Expression),)


@dataclass
class Choice(Map):
    spec: Tags = (
        Tag("choice", Expression),
        Tag("effects", Content),
        Tag("text", Expression, optional=True),
        # Tags ommited:
        # Tag("shown_effects", Sequence[ShownEffect], optional=True),
        # Tag("reusable", Expression, optional=True),
    )


@dataclass
class Print(Map):
    spec: Tags = (Tag("print", Expression),)


@dataclass
class Error(Map):
    spec: Tags = (Tag("error", Null),)


@dataclass
class Return(Map):
    spec: Tags = (Tag("return", Null),)


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
