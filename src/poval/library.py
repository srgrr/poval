from dataclasses import dataclass

import polars as pl

from poval.ast import Rule
from poval.evaluator import compile_rule
from poval.parser import parse_avl


@dataclass(frozen=True)
class LibraryRule:
    source: str
    parsed: Rule


class Poval:
    """Code-first API for Poval."""

    @staticmethod
    def compile_violation_expression(avl_rules: list[str | Rule]) -> pl.Expr:
        normalized = _normalize_rules(avl_rules)
        violation_exprs: list[pl.Expr] = []
        for index, rule in enumerate(normalized):
            compiled = compile_rule(rule.parsed)
            violation_exprs.append(
                (compiled.when & ~compiled.then).alias(f"rule_{index}_violates")
            )
        return pl.struct(*violation_exprs).alias("rule_violations")

    @staticmethod
    def evaluate(df: pl.DataFrame, avl_rules: list[str | Rule]) -> list[pl.DataFrame]:
        normalized = _normalize_rules(avl_rules)
        violations: list[pl.DataFrame] = []
        for rule in normalized:
            compiled = compile_rule(rule.parsed)
            violations.append(df.filter(compiled.when & ~compiled.then))
        return violations


def _normalize_rules(avl_rules: list[str | Rule]) -> list[LibraryRule]:
    normalized: list[LibraryRule] = []
    for avl_rule in avl_rules:
        if isinstance(avl_rule, Rule):
            normalized.append(LibraryRule(source="<rule-ast>", parsed=avl_rule))
        else:
            normalized.append(LibraryRule(source=avl_rule, parsed=parse_avl(avl_rule)))
    return normalized
