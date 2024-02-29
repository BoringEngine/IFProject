"""Test Stories

+--------------------------+--------------------------------+
| Story                    | Description                    |
+--------------------------+--------------------------------+
| hello_world              | tests PRINT                    |
| error                    | tests ERROR                    |
| simple_choice            | tests CHOICE                   |
| simple_goto              | tests GOTO                     |
| simple_choice_goto       | tests CHOICE and GOTO together |
| simple_vars              | tests Vars and IF              |
| default_var_values       | tests Vars and IF              |
| simple_gosub             | tests GOSUB                    |
+--------------------------+--------------------------------+


TODO: One for erroneous stories to test "error handling" without a complete crash
"""

from pathlib import Path

import pytest
from engine.parser import dump, parse

from tests.cases import Case, cases

TEST_FILES = Path("tests/stories").glob("*.yaml")


@cases(*[Case(file.name, file) for file in TEST_FILES])
def test_story(case):
    ast_1 = parse(case.val)
    ast_2 = parse(dump(ast_1))
    assert ast_1 == ast_2
