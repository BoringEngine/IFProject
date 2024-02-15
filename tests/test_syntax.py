from engine.exceptions import *
from engine.parser import dump, parse
from engine.syntax import *
from pytest import fixture, raises

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
    return Expression(data="test")


def test_initialization(example_expression):
    assert example_expression.data == "test"
    assert example_expression.pattern == ".*"


# Sequence ----------------------------------------------------------------


@fixture
def example_sequence():
    return Content(data=[Expression(data="test")])


def test_empty_sequence():
    empty_sequence = Sequence([])
    assert empty_sequence.data == []


def test_simple_sequence_indexing(example_sequence):
    assert example_sequence[0] == Expression(data="test")


# Map ---------------------------------------------------------------------


@fixture
def example_map():
    return A(data={"a": Expression(data="test")})


def test_get_item(example_map):
    assert example_map["a"] == Expression(data="test")


# Complex Nodes ------------------------------------------------------------


Text = Expression
Id = Expression
Address = Expression


@fixture
def example_complex_node():
    return Doc(
        data={
            "blocks": Content(
                data=[
                    Block(
                        data={
                            "name": Id(data="first_block"),
                            "content": Content(
                                data=[
                                    Print(data={"print": Text(data="hi")}),
                                    Goto(data={"goto": Address(data="/second_block")}),
                                ]
                            ),
                        }
                    ),
                    Block(
                        data={
                            "name": Id(data="second_block"),
                            "content": Content(
                                data=[
                                    If(
                                        data={
                                            "if": Expression(data="pi=3.14"),
                                            "then": Content(
                                                data=[
                                                    GoSub(data={"gosub": Null()}),
                                                    GoSub(data={"gosub": Null()}),
                                                    Expression(data="None"),
                                                ]
                                            ),
                                            "else": Content(
                                                data=[
                                                    Error(data={"error": Null()}),
                                                    Content(
                                                        data=[
                                                            Content(
                                                                data=[
                                                                    Content(
                                                                        data=[
                                                                            Expression(
                                                                                data="nested_node"
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
                                        data={
                                            "choice": Text(data=";aldkfja;"),
                                            "effects": Content(data=[]),
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


def test_get_valid_complex_indexing(example_complex_node):
    assert type(example_complex_node["blocks"]) == Content
    assert type(example_complex_node["blocks"][1]["name"]) == Expression
    assert example_complex_node["blocks"][0]["content"][0]["print"] == "hi"


def test_get_valid_complex_addressing(example_complex_node):
    assert type(example_complex_node.get_addr([])) == Doc
    assert type(example_complex_node.get_addr(["blocks"])) == Content
    assert type(example_complex_node.get_addr(["blocks", 1, "name"])) == Expression
    assert example_complex_node.get_addr(["blocks", 0, "content", 0, "print"]) == "hi"
    assert (
        type(example_complex_node.get_addr(["blocks", 0, "content", 0, "print"], 5))
        == Doc
    )
    assert (
        type(example_complex_node.get_addr(["blocks", 1, "content", 0, "then", 2]))
        == Node
    )
    assert example_complex_node.get_addr(
        ["blocks", 1, "content", 0, "else", 1, 0, 0, 0]
    ) == Expression(data="nested_node")


def test_get_address_invalid_key_raises_BadAddress(example_complex_node):
    with raises(BadAddress):
        example_complex_node.get_addr(["vars"])
    with raises(BadAddress):
        example_complex_node.get_addr(["blocks", 2])
    with raises(BadAddress):
        example_complex_node.get_addr(["blocks", "first_block"])
    with raises(BadAddress):
        example_complex_node.get_addr(["blocks", 1, "name", "data"])
    with raises(BadAddress):
        example_complex_node.get_addr(["blocks", 0, "content", 0, "print"], 6)
    with raises(BadAddress):
        example_complex_node.get_addr(["blocks", 0, "content", 0, "print"], 4)


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
    var = Variable(data="var")
    assert var.pattern == "^[a-zA-Z_][a-zA-Z0-9_]*$"


# Syntax V1
def test_v1_syntax_extension():
    assert Variable in syntax_v1.types
