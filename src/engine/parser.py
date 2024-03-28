import logging
from pathlib import Path
from types import NoneType

import logging518.config
import yaml

logging518.config.fileConfig("pyproject.toml")
log = logging.getLogger("Parser")


from engine.exceptions import NotRecognized
from engine.syntax import (
    Map,
    Node,
    NodeType,
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
        name = node_type.name
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
        return self._parse(data=popo, node_type=None)

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

    def _parse(self, data: PoPo, node_type: NodeType | None) -> Node:
        log_parse_start(data, node_type)

        match data:
            case str():
                return self._parse_value(data, node_type)
            case list():
                return self._parse_sequence(data, node_type)
            case dict():
                return self._parse_map(data, node_type)
            case None:
                return self._parse_null(data, node_type)
            case _:
                raise TypeError(f"Data: {data} does not match node {node_type}")

    def _parse_value(self, data: str, node_type: NodeType | None) -> Value:
        log.debug(f"=> Parse as value: {data}")
        if node_type is None or not issubclass(node_type, Value):
            raise TypeError(f"Expected Value, got: {node_type}")
        return node_type(data)

    def _parse_sequence(self, data: list, node_type: NodeType | None) -> Sequence:
        log.debug(f"=> Parse as sequence: {data}")
        if node_type is None or not issubclass(node_type, Sequence):
            raise TypeError(f"Expected Sequence, got: {node_type}")
        # Fix me: Implement list_of type checking
        return Sequence([self._parse(item, None) for item in data])

    def _parse_null(self, data: None, node_type: NodeType | None) -> Null:
        log.debug(f"=> Parse as null: {data}")
        if not node_type is Null:
            raise TypeError(f"Expected Null, got: {node_type}")
        if data is not None:
            raise NotRecognized(f"Unrecognized null: {data}")
        return Null()

    def _parse_map(self, data, node_type: NodeType | None) -> Map:
        candidate_nodes = [node_type] if node_type else self.syntax.maps
        log.debug(
            f"=> Parse as map. Candidate nodes: "
            "{[node.name for node in candidate_nodes]}:"
        )

        for node in candidate_nodes:
            if all(tag.key in data or tag.optional for tag in node.spec):
                log.debug(f"===> Matched tags for {node.name}.")
                result = {
                    tag.key: self._parse(data[tag.key], tag.type)
                    for tag in node.spec
                    if tag.key in data
                }
                return node(result)
        raise NotRecognized(f"Unrecognized map: {data}")

    def _dump(self, node: Node) -> PoPo:
        data, type = node.data, node.name
        match node:
            case Null():
                log.debug("Dumping Null node.")
                return None
            case Value():
                log.debug(f"Dumping {type} value: {data}")
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
