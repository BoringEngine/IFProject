from __future__ import annotations
from pathlib import Path

import re
from dataclasses import dataclass, replace
from functools import cached_property
from types import NoneType, UnionType
from typing import Any

# AST Nodes --------------------------------------------------------------------


class Node:
    """A base class for all AST nodes."""

    ...


# We need this because future __annotations__ are strings now!
# See: Bolivian tree lizard cleanup plan
value_type_map = {
    "str": str,
    "int": int,
    "bool": bool,
    "Path": Path,
}


@dataclass
class Value(Node):
    """A base class for all value nodes."""

    def __init__(self, value: Any):
        # Check the type
        _type = value_type_map[self.__annotations__["type"]]

        if not isinstance(value, _type):
            raise ValueError(f"Invalid type for {_type}: {type(value)}, value: {value}")
        # Check string patterns
        if isinstance(value, str) and hasattr(self, "pattern"):
            if not re.match(self.pattern, value):
                raise ValueError(f"Invalid value for {self.type}: {value}")
        # Run the check method
        if hasattr(self, "check"):
            self.check(value)

        self.value = value

    @property
    def type(self):
        """Return the type of the value"""
        return self.__annotations__["type"]


class List(Node):
    """A base class for all list nodes."""

    data: list
    list_of: "NodeType"

    def __init__(self, *args):
        # Check arg types
        for arg in args:
            list_type = self.__annotations__["list_of"]
            if not isinstance(arg, list_type):
                raise ValueError(
                    f"Invalid type for {self.type}-list: {type(arg)}, value: {arg}"
                )
        self.data = list(args)

    def __iter__(self):
        return iter(self.data)

    def __get_item__(self, index: int):
        return self.data[index]


@dataclass
class Tag:
    key: str
    type: Node
    optional: bool = False


class Map(Node):
    """A base class for all map nodes."""

    data: dict

    def __init__(self, **data):
        """Create a map node with the given data."""
        # Ensure required tag keys
        missing_keys = self.required_keys - data.keys()
        if missing_keys:
            raise ValueError(f"Missing required tags: {missing_keys}")

        # Check tag types
        for tag in self.spec:
            value = data.get(tag.key)
            if value is not None and not isinstance(value, tag.type):
                raise ValueError(f"Invalid type for tag {tag.key}: {type(value)}")

        self.data = data

    # Getters

    def __getitem__(self, key: str):
        """Get the value of a tag"""
        return self.data[key]

    def __getattribute__(self, key: str) -> Any:
        """Get the value of a tag or the attribute of the class"""
        # Deal with spicy tags
        key = self.normalize_key(key)

        # Get non-tag attributes
        if key not in self.keys:
            return super().__getattribute__(key)

        # Return tag value, None if it doesn't exist
        return self.data.get(key)

    def __iter__(self):
        """Iterate over the key-value pairs of the map"""
        return iter(self.data.items())

    # Tag info

    @cached_property  # Make a class property - Verify that this works
    @classmethod
    def spec(cls):
        """Hoist the tag spec from the class annotations"""
        _spec = []
        for key, value in cls.__annotations__.items():
            key = cls.normalize_key(key)

            # Required tags (name : NodeType)
            if isinstance(value, NodeType):
                _spec.append(Tag(key, value))

            # Optional tags (name : NodeType | None)
            if isinstance(value, UnionType):
                A = value.__args__[0]
                B = value.__args__[1]
                if isinstance(A, NodeType) and isinstance(B, NoneType):
                    _spec.append(Tag(key, A, optional=True))
                elif isinstance(A, NoneType) and isinstance(B, NodeType):
                    _spec.append(Tag(key, B, optional=True))
        return _spec

    @cached_property
    def keys(self):
        """Return the keys of the tags in the map"""
        return [tag.key for tag in self.spec]

    @cached_property
    def required_keys(self):
        """Return the required keys of the tags in the map"""
        return {tag.key for tag in self.spec if not tag.optional}

    def normalize_key(self, key: str):
        """Remove trailing underscores from the key"""
        # Ignore trailing dunderscores!
        # Critical for the __getattribute__ method and others
        if key.endswith("__"):
            return key

        return key.rstrip("_")


class Disjunct(Node):
    """A base class for all disjunct nodes."""

    types: NodeTypes

    def __init__(self, node: Node):
        if node.type not in self.__annotations__["types"].__args__:
            raise ValueError(f"Invalid type for disjunct: {node.type}, value: {node}")


# Syntax Objects --------------------------------------------------------------


class Syntax:
    """A container for all the syntax nodes."""

    root: NodeType
    values: ValueTypes
    lists: ListTypes
    maps: MapTypes
    disjuncts: DisjunctTypes

    @classmethod
    def __getattribute__(self, key: str) -> Any:
        """Hoist the node types from the consumer class annotations"""
        if key not in ["root", "values", "lists", "maps", "disjuncts"]:
            return super().__getattribute__(key)
        return self.__annotations__[key]


# Type Aliases ----------------------------------------------------------------

NodeType = type[Node]
NodeTypes = list[NodeType]
ValueType = type[Value]
ValueTypes = list[ValueType]
ListType = type[List]
ListTypes = list[ListType]
MapType = type[Map]
MapTypes = list[MapType]
DisjunctType = type[Disjunct]
DisjunctTypes = list[DisjunctType]
