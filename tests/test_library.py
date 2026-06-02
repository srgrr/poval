import polars as pl

from polang import Polang


RULE = """
WHEN
  ALWAYS
THEN
  ALL_EQUAL(COL(price))
GROUP BY
  "route"
"""


def test_evaluate_returns_violations_per_rule() -> None:
    df = pl.DataFrame(
        {
            "route": ["A", "A", "A", "B", "B"],
            "price": [10, 10, 12, 20, 20],
        }
    )

    violations = Polang.evaluate(df, [RULE])

    assert len(violations) == 1
    assert violations[0].height == 3
    assert set(violations[0]["route"].to_list()) == {"A"}


def test_compile_violation_expression() -> None:
    df = pl.DataFrame(
        {
            "route": ["A", "A", "A", "B", "B"],
            "price": [10, 10, 12, 20, 20],
        }
    )

    expr = Polang.compile_violation_expression([RULE])
    out = df.select(expr).unnest("rule_violations")

    assert out["rule_0_violates"].sum() == 3
