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
                if index not in self.keys:
                    raise BadAddress(f"{self.name} node has no {index} key.")
                if index in self.data:
                    return self.data[index]
                if index in self.optional_keys:
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
        self.optional = optional


class Map(Node):
    data: dict
    spec: tuple[Tag, ...]
    keys: list[str] = []
    required_keys: list[str] = []
    optional_keys: list[str] = []

    def __init__(self, data: dict):
        self.data = data

    @classmethod
    def compile(self):
        self.optional_keys = [tag.key for tag in self.spec if not tag.optional]
        for tag in self.spec:
            self.keys.append(tag.key)
            if not tag.optional:
                self.required_keys.append(tag.key)
            if isinstance(tag.type, str):
                tag.type = globals()[tag.type]


# Syntax ----------------------------------------------------------------------


class Syntax:
    types: NodeTypes

    def __init__(self, *types: NodeType):
        self.types = types
        for type in types:
            if issubclass(type, Map):
                type.compile()

    @property
    def values(self) -> NodeTypes:
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
    spec = (Tag("a", Value),)


class If(Map):
    spec = (
        Tag("if", Value),
        Tag("then", Sequence),
        Tag("else", Sequence, optional=True),
    )


class Doc(Map):
    spec = (Tag("blocks", Sequence),)


class Blocks(Sequence):
    pass


class Block(Map):
    spec = (
        Tag("name", Value),
        Tag("content", Sequence),
    )


class Content(Sequence):
    pass


class Goto(Map):
    spec = (Tag("goto", Value),)


class GoSub(Map):
    spec = (Tag("gosub", Value),)


class Choice(Map):
    spec = (
        Tag("choice", Value),
        Tag("effects", Content),
        Tag("text", Value, optional=True),
        # Tags ommited:
        # Tag("shown_effects", Sequence[ShownEffect], optional=True),
        # Tag("reusable", Value, optional=True),
    )


class Print(Map):
    spec = (Tag("print", Value),)


class Error(Map):
    spec = (Tag("error", Null),)


class Return(Map):
    spec = (Tag("return", Null),)


class Wait(Map):
    spec = (Tag("wait", Null),)


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
