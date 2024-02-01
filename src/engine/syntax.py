import types
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import yaml

# Base Nodes ------------------------------------------------------------------


class Node:
    @property
    def type(self):
        return self.__class__.__name__


NodeType = type[Node]
NodeTypes = tuple[NodeType]


class NodeRef:
    name: str
    ...


class ExpressionRef(NodeRef):
    ...


class SequenceRef(NodeRef):
    ...


class MapRef(NodeRef):
    name: str
    type: str


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

    def __getitem__(self, key: str) -> Any:
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
class Variable(Expression):
    pattern: str = "^[a-zA-Z_][a-zA-Z0-9_]*$"


simple_syntax = initial_syntax.extend(If, A, Variable)


node_class_dict = {
    "A": A,
}


def load_syntax(syntax_file: Path):
    syntax_str = Path.read_text()
    syntax_dict = yaml.load(syntax_str, Loader=yaml.FullLoader)


node_class_dict = {
    "A": A,
}


def load_syntax(syntax_file: Path):
    syntax_str = Path.read_text()
    syntax_dict = yaml.load(syntax_str, Loader=yaml.FullLoader)

    for tag, tag_obj in syntax_dict.items():
        node_class = types.new_class(tag_obj["name"], bases=(Map))
        # Unpack spec
        for tag in tag_obj.spec:
            value_class = node_class_dict[tag["type"]]
            tag = Tag(
                key=tag["name"],
                type=value_class,
                optional=tag.get("optional, False"),
            )
            node_class.spec.append(tag)
        # Unpack only_one
        for item_name, item_type in tag_obj["only_one"].items():
            key = item_name
            node_class = node_class_dict[item_type]
            tag = Tag(key, node_class)
            node_class.only_one.append(tag)


def load_map_A(map_dict: dict):
    node_item = Map()
    # Unpack spec
    for item in map_dict["spec"]:
        key = item["name"]
        node_class = node_class_dict[item["type"]]
        optional = item.get("optional, False")
        tag = Tag(key, node_class, optional)
        node_item.spec.append(tag)
    # Unpack only_one
    for item_name, item_type in map_dict["only_one"].items():
        key = item_name
        node_class = node_class_dict[item_type]
        tag = Tag(key, node_class)
        node_item.only_one.append(tag)


def load_map_B(map_dict: dict):
    node_class = Map()
    # Unpack required
    for name, type in map_dict["required"].items():
        node_class = node_class_dict[type]
        tag = Tag(name, node_class)
        node_class.spec.append(tag)
    # Unpack required
    for name, type in map_dict["optional"].items():
        node_class = node_class_dict[type]
        tag = Tag(name, node_class, optional=True)
        node_class.spec.append(tag)
    # Unpack only_one
    for name, type in map_dict["only_one"].items():
        node_class = node_class_dict[type]
        tag = Tag(name, node_class)
        node_class.only_one.append(tag)
