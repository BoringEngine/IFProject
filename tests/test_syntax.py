from engine.exceptions import *
from engine.parser import dump, parse
from engine.syntax import *
from pytest import fixture, raises

from tests.cases import Case, cases

# Test Basic Nodes ------------------------------------------------------------


# Node
@fixture
def example_node():
    return Node()


def test_type_property(example_node):
    assert example_node.type == "Node"


# Expression --------------------------------------------------------------


@fixture
def example_expression():
    return Expression("test")


def test_initialization(example_expression):
    assert example_expression.data == "test"
    assert example_expression.pattern == ".*"


# Sequence ----------------------------------------------------------------


@fixture
def example_sequence():
    return Content([Expression("test")])


def test_empty_sequence():
    empty_sequence = Sequence([])
    assert empty_sequence.data == []


# Map ---------------------------------------------------------------------


@fixture
def example_map():
    return A({"a": Expression("test")})


# Complex Nodes ------------------------------------------------------------


Text = Expression
Id = Expression
Address = Expression


@fixture
def example_complex_node():
    return Doc(
        {
            "blocks": Content(
                [
                    Block(
                        {
                            "name": Id("first_block"),
                            "content": Content(
                                [
                                    Print({"print": Text("hi")}),
                                    Goto({"goto": Address("/second_block")}),
                                ]
                            ),
                        }
                    ),
                    Block(
                        {
                            "name": Id("second_block"),
                            "content": Content(
                                [
                                    If(
                                        {
                                            "if": Expression("pi=3.14"),
                                            "then": Content(
                                                [
                                                    GoSub({"gosub": Address("home")}),
                                                    GoSub({"gosub": Address("sleep")}),
                                                    Expression("days += 1"),
                                                ]
                                            ),
                                            "else": Content(
                                                [
                                                    Error({"error": Null()}),
                                                    Content(
                                                        [
                                                            Content(
                                                                [
                                                                    Content(
                                                                        [
                                                                            Expression(
                                                                                "nested_node"
                                                                            )
                                                                        ]
                                                                    )
                                                                ]
                                                            )
                                                        ]
                                                    ),
                                                ]
                                            ),
                                        }
                                    ),
                                    Choice(
                                        {
                                            "choice": Text(";aldkfja;"),
                                            "effects": Content([]),
                                        }
                                    ),
                                ]
                            ),
                        }
                    ),
                ]
            )
        }
    )


@fixture
def complex_node_yaml():
    return """
        blocks:
        - content:
        - print: hi
        - goto: /second_block
        name: first_block
        - content:
        - else:
            - error: null
            - - - - nested_node
            if: pi=3.14
            then:
            - gosub: null
            - gosub: null
            - None
        - choice: ;aldkfja;
            effects: []
        name: second_block
    """


def test_dump_complex_node(example_complex_node):
    dump(example_complex_node)


class TestGetItem:
    ...

    def test_sequence_indexing(self, example_sequence):
        assert example_sequence[0] == Expression("test")

    def test_map_indexing(self, example_map):
        assert example_map["a"] == Expression("test")

    def test_complex_indexing(self, example_complex_node):
        assert type(example_complex_node["blocks"]) == Content

    def test_nested_indexing(self, example_complex_node):
        assert example_complex_node["blocks"][0]["content"][0]["print"] == Text("hi")

    @cases(
        Case("Invalid Map Index", "vars"),
        Case("Invalid Map Index Not Str", 1),
    )
    def test_invalid_map_index(self, case, example_map):
        with raises(BadAddress):
            example_map[case.val]

    def test_invalid_expression_index(self, example_complex_node):
        with raises(BadAddress):
            example_complex_node["blocks"][0]["name"]["data"]

    @cases(
        Case("Invalid Sequence Index Too Big", 1),
        Case("Invalid Sequence Index Negative", -1),
        Case("Invalid Sequence Index Not Int", "a"),
    )
    def test_invalid_sequence_index(self, case, example_sequence):
        with raises(BadAddress):
            example_sequence[case.val]


class TestGetAddr:
    @cases(
        Case("Empty Address", [], Doc),
        Case("Simple Address", ["blocks"], Content),
        Case("Simple Address with Index", ["blocks", 1, "name"], Expression),
    )
    def test_valid_addresses_by_types(self, case, example_complex_node):
        result = example_complex_node.get_addr(case.val)
        assert isinstance(result, case.expects)

    @cases(
        Case("Terminal Address", ["blocks", 0, "content", 0, "print"], Text("hi")),
        Case(
            "Nested Address",
            ["blocks", 1, "content", 0, "else", 1, 0, 0, 0],
            Expression("nested_node"),
        ),
    )
    def test_valid_address_by_vals(self, case, example_complex_node):
        result = example_complex_node.get_addr(case.val)
        assert result == case.expects

    @cases(
        Case("Required key does not exist", ["vars"]),
        Case("Sequence index Too Big", ["blocks", 2]),
        Case("Sequence index Negative", ["blocks", -1]),
        Case("Sequence index Not Int", ["blocks", "first_block"]),
        Case("Terminal node has no subnodes", ["blocks", 0, "name", "data"]),
    )
    def test_invalid_addresses(self, case, example_complex_node):
        with raises(BadAddress):
            example_complex_node.get_addr(case.val)


# Simple Syntax ------------------------------------------------------------


def test_empty_syntax():
    assert not empty_syntax.expressions
    assert not empty_syntax.sequences
    assert not empty_syntax.maps


def test_simple_syntax_extension():
    assert If in simple_syntax.types
    assert A in simple_syntax.types


# Variable -----------------------------------------------------------------


def test_pattern():
    var = Variable("var")
    assert var.pattern == "^[a-zA-Z_][a-zA-Z0-9_]*$"


# Syntax V1
def test_v1_syntax_extension():
    assert Variable in syntax_v1.types
