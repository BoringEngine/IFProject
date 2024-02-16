from typing import Any, Generator, NamedTuple

import pytest


class Case(NamedTuple):
    name: str
    val: Any | None = None
    expects: Any | None = None


def normalize(val):
    """Normalize a value to a tuple."""
    if isinstance(val, tuple):
        if len(val) == 1:
            raise ValueError("Tuple with one element is not allowed.")
        return val
    return (val,)


def case_list(*cases: Case):
    """
    Parametrize a test with a list of cases.

    The cases should be a list of Case tuples:
    case_list(
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


def cases(cases: dict[str, Any | tuple[Any, Any]]):
    """Parametrize a test with a dictionary of cases.

    The dictionary should have the form:
    {
        "name": (val, expects),
        "name": val,
    }
    """

    return case_list(*[Case(name, *normalize(val)) for name, val in cases.items()])
