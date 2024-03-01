from typing import NamedTuple

import pytest
from engine.parser import Parser
from engine.syntax import A, If, Node, Sequence, Value

from .cases import Case, cases

class MyTestCase:
    val: str
    expected: Node


@pytest.fixture
def test_cases():
    class a_obj(MyTestCase):
        val = "a: action"
        expects = A(data={"a": Value(data="action")})

    class if_obj(MyTestCase):
        val = """
    if: condition1
    then:
    - a: action1
    else:
    - a: action2
    """
        expects = If(
            {
                "if": Value(data="condition1"),
                "then": Sequence(
                    [
                        A(data={"a": Value(data="action1")}),
                    ]
                ),
                "else": Sequence(
                    [
                        A(data={"a": Value(data="action2")}),
                    ]
                ),
            }
        ),
    ),
)


@sample_node_cases
def test_parse(case):
    node = parse(case.val)
    assert node == case.expects


@sample_node_cases
def test_dump(case):
    yaml = dump(case.expects)
    node = parse(yaml)

    assert node == case.expects
