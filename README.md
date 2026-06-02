# poval

`poval` is a small rule language and Python library for dataframe validation.
You write rules in a readable DSL and evaluate them against Polars dataframes.

The project provides:

- A parser for the `WHEN` / `THEN` / `GROUP BY` rule format
- A typed AST representation of rules
- An evaluator that compiles rules into Polars expressions
- A code-first API via `Poval`

## Install

```bash
pip install -e .
```

## Rule format

```text
WHEN
    <bool_expr>
THEN
    <bool_expr>
GROUP BY
    "col1", "col2"
```

Each rule has:

- `WHEN`: selects the rows the rule applies to
- `THEN`: condition that must be true for selected rows
- `GROUP BY`: grouping keys used by group-aware expressions such as `ALL_EQUAL`

Supported expressions:

- Boolean literals: `ALWAYS`, `NEVER`, `TRUE`, `FALSE`
- Boolean operators: `AND`, `OR`, `NOT`
- Column references: `COL(name)`
- Comparisons: `<`, `<=`, `>`, `>=`, `=`, `!=`
- Null checks: `COL(name) IS NULL`, `COL(name) IS NOT NULL`
- Group consistency: `ALL_EQUAL(COL(name))`
- Variadic boolean helpers: `ANY(expr1, expr2, ...)`, `ALL(expr1, expr2, ...)`
- Literals: positive integers and double-quoted strings

## Python API

```python
import polars as pl
from poval import Poval

rule = """
WHEN
  ALWAYS
THEN
  ALL_EQUAL(COL(price))
GROUP BY
  "route"
"""

df = pl.DataFrame(
    {
        "route": ["A", "A", "A", "B", "B"],
        "price": [10, 10, 12, 20, 20],
    }
)

violations = Poval.evaluate(df, [rule])
print(violations[0])
```

Main entrypoints:

- `Poval.evaluate(df, rules)`: returns one dataframe of violating rows per rule
- `Poval.compile_violation_expression(rules)`: returns a Polars struct expression with per-rule violation flags
