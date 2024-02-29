from typing import Any, Generator, NamedTuple

import pytest


class Case(NamedTuple):
    name: str
    val: Any | None = None
    expects: Any | None = None


def cases(*cases: Case):
    """
    Parametrize a test with a list of cases.

    The cases should be a list of Case tuples:
    cases(
        Case(name, val, expects),
        Case(name, val, expects),
        ...
    )
    """
    return pytest.mark.parametrize(
        "case",
        cases,
        ids=lambda case: case.name,
    )
