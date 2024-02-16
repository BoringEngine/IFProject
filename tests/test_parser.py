from typing import NamedTuple

import pytest
from engine.parser import dump, parse
from engine.syntax import A, Expression, If, Node, Sequence


class Case(NamedTuple):
    name: str
    val: str
    expects: Node


test_cases = pytest.mark.parametrize(
    "case",
    [
        Case(
            name="A Node",
            val="a: action",
            expects=A({"a": Expression("action")}),
        ),
        Case(
            name="If Node",
            val="""
                if: condition1
                then:
                - a: action1
                else:
                - a: action2
            """,
            expects=If(
                {
                    "if": Expression("condition1"),
                    "then": Sequence([A({"a": Expression("action1")})]),
                    "else": Sequence([A({"a": Expression("action2")})]),
                }
            ),
        ),
    ],
    ids=lambda case: case.name,
)


@test_cases
def test_parse(case):
    node = parse(case.val)
    assert node == case.expects


@test_cases
def test_dump(case):
    yaml = dump(case.expects)
    node = parse(yaml)

    assert node == case.expects
