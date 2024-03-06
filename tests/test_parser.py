from typing import NamedTuple

import pytest
from engine.parser import dump, parse
from engine.syntax import A, If, Node, Sequence, Value

from .cases import Case, cases

sample_node_cases = cases(
    Case(
        name="A Node",
        val="a: action",
        expects=A({"a": Value("action")}),
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
                "if": Value("condition1"),
                "then": Sequence([A({"a": Value("action1")})]),
                "else": Sequence([A({"a": Value("action2")})]),
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
