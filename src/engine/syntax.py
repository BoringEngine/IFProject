from typing import Any

from engine.exceptions import BadAddress, BadNode

# Base Nodes ------------------------------------------------------------------


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

    def __getitem__(self, index: int | str | None = None):
        match self:
            case Sequence():
                if not isinstance(index, int):
                    raise BadAddress(f"Index {index} must be an integer.")
                if index < 0:
                    raise BadAddress(f"Negative index {index} is not allowed.")
                if index + 1 > len(self.data):
                    raise BadAddress(f"No subnode at index {index} in node {self}.")
                return self.data[index]

            case Map():
                if not isinstance(index, str):
                    raise BadAddress(f"Map node requires string index. Given: {index}.")
                if index not in self.spec.keys:
                    raise BadAddress(f"{self.name} node has no {index} key.")
                if index in self.data:
                    return self.data[index]
                if index in self.spec.optional_keys:
                    return None  # Should this be Null?
                raise BadNode("{self.type} Map node missing a required key: {key}")

            case Value() | Null():
                if index is not None:
                    raise BadAddress("Terminal {self.type} accessed with index {index}")
                return self.data

    @property
    def name(self):
        return self.__class__.__name__

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


NodeType = type[Node]
NodeTypes = tuple[NodeType, ...]


class Value(Node):
    data: str
    pattern: str = ".*"

    def __init__(self, data: str):
        self.data = data

    def __getitem__(self, index: Any = None):
        if index is not None:
            raise BadAddress("Terminal {self.type} accessed with index {index}")


class Sequence(Node):
    data: list

    def __init__(self, data: list):
        self.data = data


class Tag:
    key: str
    type: NodeType | str
    optional: bool = False

    def __init__(self, key: str, type: NodeType | str, optional: bool = False):
        self.key = key
        self.type = type
        self.optional


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


class Map(Node):
    data: dict
    spec: Spec

    def __init__(self, data: dict):
        self.data = data


# Syntax ----------------------------------------------------------------------


class Syntax:
    types: NodeTypes

    def __init__(self, *types: NodeType):
        self.types = types

    @property
    def expressions(self) -> NodeTypes:
        return self.by_type(Value)

    @property
    def sequences(self) -> NodeTypes:
        return self.by_type(Sequence)

    @property
    def maps(self) -> NodeTypes:
        return self.by_type(Map)

    def by_type(self, target_type: NodeType) -> NodeTypes:
        return tuple(t for t in self.types if issubclass(t, target_type))


# Basic Syntax ----------------------------------------------------------------


class Null(Node):
    data: None = None


class A(Map):
    spec = Spec(
        Tag("a", Value),
    )


class If(Map):
    spec = Spec(
        Tag("if", Value),
        Tag("then", Sequence),
        Tag("else", Sequence, optional=True),
    )


class Doc(Map):
    spec = Spec(
        Tag("blocks", Sequence),
    )


class Blocks(Sequence):
    pass


class Block(Map):
    spec = Spec(
        Tag("name", Value),
        Tag("content", Sequence),
    )


class Content(Sequence):
    pass


class Goto(Map):
    spec = Spec(
        Tag("goto", Value),
    )


class GoSub(Map):
    spec = Spec(
        Tag("gosub", Value),
    )


class Choice(Map):
    spec = Spec(
        Tag("choice", Value),
        Tag("effects", Content),
        Tag("text", Value, optional=True),
        # Tags ommited:
        # Tag("shown_effects", Sequence[ShownEffect], optional=True),
        # Tag("reusable", Expression, optional=True),
    )


class Print(Map):
    spec = Spec(
        Tag("print", Value),
    )


class Error(Map):
    spec = Spec(
        Tag("error", Null),
    )


class Return(Map):
    spec = Spec(
        Tag("return", Null),
    )


class Wait(Map):
    spec = Spec(
        Tag("wait", Null),
    )


class Variable(Value):
    pattern: str = "^[a-zA-Z_][a-zA-Z0-9_]*$"


class Text(Value):
    pattern: str = "[a-zA-Z_]*"


simple_syntax = Syntax(
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
