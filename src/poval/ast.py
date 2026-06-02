from dataclasses import dataclass
from typing import Literal, Union

CompareOp = Literal["<", "<=", ">", ">=", "=", "!="]
Expr = Union["ColExpr", "IntLiteral", "StringLiteral"]
BoolExpr = Union[
    "BoolTrue",
    "BoolFalse",
    "BoolNot",
    "BoolAnd",
    "BoolOr",
    "CompareExpr",
    "AllEqualExpr",
    "AnyExpr",
    "AllExpr",
    "IsNullExpr",
    "ColExpr",
    "IntLiteral",
    "StringLiteral",
]


@dataclass(frozen=True)
class BoolTrue:
    pass


@dataclass(frozen=True)
class BoolFalse:
    pass


@dataclass(frozen=True)
class BoolNot:
    operand: BoolExpr


@dataclass(frozen=True)
class BoolAnd:
    left: BoolExpr
    right: BoolExpr


@dataclass(frozen=True)
class BoolOr:
    left: BoolExpr
    right: BoolExpr


@dataclass(frozen=True)
class CompareExpr:
    left: Expr
    op: CompareOp
    right: Expr


@dataclass(frozen=True)
class ColExpr:
    name: str


@dataclass(frozen=True)
class AllEqualExpr:
    col: ColExpr


@dataclass(frozen=True)
class IsNullExpr:
    col: ColExpr
    negated: bool = False


@dataclass(frozen=True)
class AnyExpr:
    operands: list[BoolExpr]


@dataclass(frozen=True)
class AllExpr:
    operands: list[BoolExpr]


@dataclass(frozen=True)
class IntLiteral:
    value: int


@dataclass(frozen=True)
class StringLiteral:
    value: str


@dataclass(frozen=True)
class Rule:
    when: BoolExpr
    then: BoolExpr
    group_by: list[str]
