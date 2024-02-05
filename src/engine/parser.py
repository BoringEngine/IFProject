import types
from pathlib import Path
from typing import Any

import yaml

from engine.exceptions import NotRecognized
from engine.syntax import (
    List,
    ListType,
    Map,
    MapType,
    Node,
    NodeType,
    Syntax,
    SyntaxV1,
    Value,
    ValueType,
)

PoPo = str | list | dict


class Parser:
    """A Parser that can parse Yaml into AST Nodes and back again."""

    def __init__(self, syntax: Syntax):
        self.syntax = syntax

    def parse(self, data: str | Path) -> Node:
        """Parse a YAML string or file into an AST Node."""
        # Read the file if given
        if isinstance(data, Path):
            data = data.read_text()
        # Parse the file into a PoPo
        data = yaml.safe_load(data)
        # Parse the PoPo into a Node
        return self.parse_popo(data, self.syntax.root)

    def dump(self, node: Node, file: Path | None = None) -> str:
        """Dump an AST Node into a YAML string or file."""

        # Recursively dump the node into a PoPo
        def _dump(node: Node) -> PoPo:
            match node:
                case Value():
                    return node.value
                case Map():
                    return {k: _dump(v) for k, v in node._data.items}
                case List():
                    return [_dump(item) for item in node._data]
                case Node():
                    raise NotRecognized(f"Unrecognized node: {node}")
                case _:
                    raise TypeError(f"Expected Node, got: {type(node)}")

        # Dump the PoPo into a YAML string
        result = yaml.dump(self._dump(node))

        # Write the result to file, if given
        if file:
            file.write_text(result)

        return result

    # Private methods

    def parse_popo(self, data: PoPo, node_type: NodeType) -> Node:
        # Hack to match node types with class patterns
        node_type_instance = node_type.__new__(node_type) if node_type else None

        match data, node_type_instance:
            case str(), Value():
                return self.parse_value(data, node_type)

            case list(), List():
                return self.parse_list(data, node_type)

            case dict(), None | Map():
                return self.parse_map(data, node_type)

            case _:
                raise TypeError(f"Data: {data} does not match node {node_type}")

    def parse_value(self, data: str, node_type: ValueType) -> Value:
        return node_type(data)

    def parse_list(self, parsed_data, node_type: ListType) -> List:
        # Check arg types early
        for item in parsed_data:
            if not isinstance(item, node_type.list_of):
                raise NotRecognized(
                    f"Invalid type for {node_type}-list: {type(item)}, value: {item}"
                )

        parsed_data = (self.parse_popo(item, node_type.list_of) for item in parsed_data)
        return node_type(*parsed_data)

    def parse_map(self, data, node_type: MapType | None) -> Map:
        candidate_nodes = [node_type] if node_type else self.syntax.maps
        for node in candidate_nodes:
            # Ensure all required tags are present
            if not all(tag.key in data or tag.optional for tag in node.spec):
                continue
            # Parse tag values
            result = {
                tag.key: self.parse_popo(data[tag.key], tag.type)
                for tag in node.spec
                if tag.key in data
            }
            return node(result)
        raise NotRecognized(f"Unrecognized map: {data}")


# Publish the default parser
parser = Parser(SyntaxV1)
parse = parser.parse
dump = parser.dump
