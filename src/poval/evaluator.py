from dataclasses import dataclass

import polars as pl

from poval.ast import (
    AllEqualExpr,
    AllExpr,
    AnyExpr,
    BoolAnd,
    BoolExpr,
    BoolFalse,
    BoolNot,
    BoolOr,
    BoolTrue,
    ColExpr,
    CompareExpr,
    CompareOp,
    Expr,
    IntLiteral,
    IsNullExpr,
    Rule,
    StringLiteral,
)

_COMPARE_OPS: dict[CompareOp, type] = {
    "<": pl.Expr.lt,
    "<=": pl.Expr.le,
    ">": pl.Expr.gt,
    ">=": pl.Expr.ge,
    "=": pl.Expr.eq,
    "!=": pl.Expr.ne,
}


@dataclass(frozen=True)
class CompiledRule:
    when: pl.Expr
    then: pl.Expr
    group_by: list[str]


def compile_rule(rule: Rule) -> CompiledRule:
    group_by = list(rule.group_by)
    return CompiledRule(
        when=compile_bool(rule.when, group_by=group_by),
        then=compile_bool(rule.then, group_by=group_by),
        group_by=group_by,
    )


def compile_bool(expr: BoolExpr, *, group_by: list[str]) -> pl.Expr:
    if isinstance(expr, BoolTrue):
        return pl.lit(True)
    if isinstance(expr, BoolFalse):
        return pl.lit(False)
    if isinstance(expr, BoolNot):
        return ~compile_bool(expr.operand, group_by=group_by)
    if isinstance(expr, BoolAnd):
        return compile_bool(expr.left, group_by=group_by) & compile_bool(
            expr.right, group_by=group_by
        )
    if isinstance(expr, BoolOr):
        return compile_bool(expr.left, group_by=group_by) | compile_bool(
            expr.right, group_by=group_by
        )
    if isinstance(expr, CompareExpr):
        left = compile_value(expr.left)
        right = compile_value(expr.right)
        return _COMPARE_OPS[expr.op](left, right)
    if isinstance(expr, AllEqualExpr):
        if not group_by:
            msg = "ALL_EQUAL requires at least one GROUP BY column"
            raise ValueError(msg)
        return compile_column(expr.col).n_unique().over(group_by) == 1
    if isinstance(expr, AnyExpr):
        if not expr.operands:
            return pl.lit(False)
        result = compile_bool(expr.operands[0], group_by=group_by)
        for operand in expr.operands[1:]:
            result = result | compile_bool(operand, group_by=group_by)
        return result
    if isinstance(expr, AllExpr):
        if not expr.operands:
            return pl.lit(True)
        result = compile_bool(expr.operands[0], group_by=group_by)
        for operand in expr.operands[1:]:
            result = result & compile_bool(operand, group_by=group_by)
        return result
    if isinstance(expr, IsNullExpr):
        col_expr = compile_column(expr.col)
        return col_expr.is_not_null() if expr.negated else col_expr.is_null()
    if isinstance(expr, ColExpr):
        return compile_column(expr).is_not_null()
    if isinstance(expr, IntLiteral):
        return pl.lit(expr.value)
    if isinstance(expr, StringLiteral):
        return pl.lit(expr.value)
    msg = f"unsupported expression: {type(expr).__name__}"
    raise TypeError(msg)


def compile_value(expr: Expr) -> pl.Expr:
    if isinstance(expr, ColExpr):
        return compile_column(expr)
    if isinstance(expr, IntLiteral):
        return pl.lit(expr.value)
    if isinstance(expr, StringLiteral):
        return pl.lit(expr.value)
    msg = f"unsupported value expression: {type(expr).__name__}"
    raise TypeError(msg)


def compile_column(col: ColExpr) -> pl.Expr:
    return pl.col(col.name)
