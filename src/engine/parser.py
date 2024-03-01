import logging
from pathlib import Path
from types import NoneType
from typing import overload

import logging518.config
import yaml

logging518.config.fileConfig("pyproject.toml")
log = logging.getLogger("Parser")


from engine.exceptions import NotRecognized
from engine.syntax import (
    Map,
    Node,
    Nodes,
    NodeTuple,
    Null,
    Sequence,
    Syntax,
    Value,
    syntax_v1,
)

PoPo = str | list | dict | None


def log_parse_start(data, node_type):
    # Hack to get node name for logging
    if node_type is None:
        name = "None"
    elif node_type is NoneType:
        name = "NoneType"
    else:
        name = node_type.__name__
    data_string = str(data).strip()[:80]
    log.debug(f"Parsing {name} node with: {data_string}")


class Parser:
    """A Parser that can parse Yaml or PoPo into AST Nodes and back again.

    Public Methods:
        parse: Parse a YAML string or file into an AST Node.
        dump: Dump an AST Node into a YAML string.

    Private Methods:
        _parse: Parse a PoPo into an AST Node according to the given node_type.
        _parse_map: Parse a dictionary into a Map node.
        _dump: Dump an AST Node back into a PoPo.
    """

    def __init__(self, syntax: Syntax = syntax_v1):
        """Initialize the Parser with a given syntax.

        Args:
            syntax (Syntax, optional): The syntax to use when parsing.
                Defaults to syntax_v1.
        """
        self.syntax = syntax

    def parse(self, data: str | Path) -> Node:
        """Parse a YAML string or file into an AST Node.

        Args:
            data (str | Path): The YAML data string or file to parse.

        Returns:
            Node: An AST Node that represents the parsed YAML data.

        Raises:
            NotRecognized: If the data is not recognized.
        """
        if isinstance(data, Path):
            data = data.read_text()

        popo = yaml.load(data, Loader=yaml.FullLoader)
        return self._parse_map(popo, node_type=None)

    def dump(self, node: Node, file: Path | None = None) -> str:
        """Dump an AST Node into a YAML string.

        Args:
            node (Node): The AST Node to dump.
            file (Path, optional): The file to dump the YAML string to.

        Returns:
            str: A string that represents the YAML format of the AST Node.

        Effects:
            Writes the YAML string to the given file.
        """
        result = yaml.dump(self._dump(node))

        if file:
            file.write_text(result)

        return result

    def _parse(self, data: PoPo, node_type: Nodes | None) -> Node:
        log_parse_start(data, node_type)

        match data:
            case str():
                return self._parse_expression(data, node_type)

            case list():
                return self._parse_sequence(data, node_type)

            case dict():
                return self._parse_map(data, node_type)

            case None:
                return self._parse_null(data, node_type)

            case _:
                raise TypeError(f"Data: {data} does not match node {node_type}")

    def _parse_null(self, data: None, node_type: Nodes | None) -> Null:
        if node_type is None:
            raise NotRecognized(f"Failed to provide type for null: {data}")
        if node_type is not Null:
            raise NotRecognized(f"Unexpected null. Expected {node_type.__name__}")
        log.debug(f"=> Parsing null.")
        return Null()

    def _parse_expression(self, data: str, node_type: Nodes | None) -> Value:
        if node_type is None:
            raise NotRecognized(f"Failed to provide type for expression: {data}")

        if not issubclass(node_type, Value):
            raise NotRecognized(f"Expected expression, got {node_type.__name__}")

        log.debug(f"=> Parsing expression with {node_type.__name__}.")
        return node_type(data)

    def _parse_sequence(self, data: list[PoPo], node_type: Nodes | None) -> Sequence:
        if node_type is None:
            raise NotRecognized(f"Failed to provide type for sequence: {data}")

        if not issubclass(node_type, Sequence):
            raise NotRecognized(f"Expected sequence, got {node_type.__name__}")

        log.debug(f"=> Parsing sequence with {node_type.__name__}.")
        return node_type([self._parse(item, node_type.list_of) for item in data])

    def _parse_map(self, data: dict[str, PoPo], node_type: Nodes | None) -> Map:
        if node_type is None or node_type is Node:
            if node_type is Node:
                log.warn(
                    "Deprecated: Use of Node as node_type."
                    "Caused by generic sequence. Use Contents sequence instead."
                )

            # This is fine, we'll try to match the tags to a node type.
            node_type = None
        elif not issubclass(node_type, Map):
            raise NotRecognized(f"Expected map, got {node_type.__name__}")

        candidate_nodes: NodeTuple = (node_type,) if node_type else self.syntax.maps

        for node in candidate_nodes:
            if all(tag.key in data or tag.optional for tag in node.spec):
                log.debug(f"===> Matched tags for {node.__name__}.")
                break
        else:
            raise NotRecognized(
                f"Unrecognized map: {data}, "
                "candidate nodes: {[node.type for node in candidate_nodes]}"
            )

        log.debug(f"Parsing {node.type}")

        result = {}
        for tag in node.spec:
            if tag.key in data:
                result[tag.key] = self._parse(data[tag.key], tag.type)

        return node(result)

    def _dump(self, node: Node) -> PoPo:
        data, type = node.data, node.type
        match node:
            case Null():
                log.debug("Dumping Null node.")
                return None
            case Value(data):
                log.debug(f"Dumping {type} expression: {data}")
                return data
            case Map():
                log.debug(f"Dumping {type} map: {data}")
                return {k: self._dump(v) for k, v in data.items()}
            case Sequence():
                log.debug(f"Dumping {type} sequence: {data}")
                return [self._dump(item) for item in data]
            case Node():
                raise NotRecognized(f"Unrecognized {type} node: {node}")
            case _:
                raise TypeError(f"Expected Node, got: {node}")


# Publish the default parser
parser = Parser()
parse = parser.parse
dump = parser.dump
