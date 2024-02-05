from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from engine.ast import *

# Value Nodes -----------------------------------------------------------------


class Id(Value):
    type: str
    pattern = "^[a-zA-Z0-9_-]+$"


class Address(Value):
    type: str
    pattern = "^[a-zA-Z_]+[a-zA-Z0-9_.]+$"


class Text(Value):
    type: str


class Bool(Value):
    type: bool


class Expression(Value):
    type: str

    def check(self, value: str):
        # Test the value is valid python
        try:
            ast.parse(value)
        except SyntaxError as e:
            raise ValueError(f"Invalid expression: {value}") from e

    def eval(self, context: dict):
        if context is None:
            raise ValueError("Context is required to evaluate an expression")
        return eval(self.value, context)


class UInt(Value):
    type: int

    def check(self, value: int):
        if value < 0:
            raise ValueError(f"Invalid value for uint: {value}")


class FilePath(Value):
    type: Path


# Doc


class Doc(Map):
    vars: Vars
    blocks: Blocks


class Blocks(List):
    list_of: Block


class Block(Map):
    name: Id
    start: Bool | None
    img: FilePath | None
    content: Content | None
    blocks: Blocks | None
    _one_of = "content", "blocks"


class Vars(List):
    list_of: Var


class Var(Map):
    name: Id
    type: ValueType
    value: Value | None


# Contents / Commands


class Content(List):
    list_of: StoryCommand


class StoryCommand(Disjunct):
    types: (
        Choice
        | Error
        | GoSub
        | GoTo
        | If
        | IfList
        | Modify
        | Print
        | Return
        | Switch
        | Wait
    )


# Choice


class Choice(Map):
    choice: Id
    effects: Content
    text: Text | None
    reusable: Bool | None
    shown_effects: ShownEffects | None


class ShownEffects(List):
    list_of: ShownEffect


class ShownEffect(Disjunct):
    types: GainEffect | PayEffect


class GainEffect(Map):
    gain: Id
    amount: UInt


class PayEffect(Map):
    pay: Id
    amount: UInt


# Goto / GoSub


class GoSub(Map):
    gosub: Address


class GoTo(Map):
    goto: Address


# If


class If(Map):
    _if: Expression
    then: Content
    _else: Content | None


class IfList(Map):
    if_list: Ifs


class Ifs(List):
    list_of: If


# Switch


class Switch(Map):
    switch: Id
    cases: List


class Cases(List):
    list_of: Case


class Case(Map):
    case: Value
    then: List


# Modify


class Modify(Map):
    modify: Id
    add: Expression | None
    subtract: Expression | None
    multiply: Expression | None
    divide: Expression | None
    set: Expression | None
    _one_of = "add", "subtract", "multiply", "divide", "set"


# Other Commands


class Error(Map):
    error: None


class Print(Map):
    print: Text


class Return(Map):
    return_: None


class Wait(Map):
    wait: None


# Syntax ----------------------------------------------------------------------


class SyntaxV1(Syntax):
    root: NodeType = Doc
    values: ValueTypes = [Id, Address, Text, Bool, Expression, UInt, FilePath]
    lists: ListTypes = [Vars, Blocks, Content, ShownEffects, Ifs, Cases]
    maps: MapTypes = [
        Doc,
        Var,
        Block,
        Choice,
        GainEffect,
        PayEffect,
        GoSub,
        GoTo,
        If,
        IfList,
        Modify,
        Print,
        Return,
        Switch,
        Case,
        Error,
        Wait,
    ]
    disjuncts: NodeTypes = [ShownEffect, StoryCommand]
